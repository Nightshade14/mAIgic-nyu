"""TODO: Add docstring."""

import asyncio
import enum
import logging
import os
import re
from concurrent.futures import Future, ProcessPoolExecutor
from datetime import datetime
from pprint import pformat
from queue import Queue
from typing import Any, TypeVar

from slack_bolt.adapter.socket_mode.aiohttp import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from assistant import Assistant
from maigic_nyu.db.api import DB, Item

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

app = AsyncApp(token=os.environ["SLACK_BOT_TOKEN"])


class OP(enum.Enum):
    """TODO: Add docstring."""

    fetch = enum.auto()
    handle_one = enum.auto()


T = TypeVar("T")


class Server:
    """TODO: Add docstring."""

    pool: ProcessPoolExecutor

    def __init__(self) -> None:
        """TODO: Add docstring."""
        self.assistant = Assistant()
        app.message()(self.message_hello)

        self.queue = Queue()

    async def await_future(self, future: Future[T]) -> T:
        """TODO: Add docstring."""
        done = asyncio.Event()
        future.add_done_callback(lambda _: done.set())
        await done.wait()
        return future.result()

    async def _slack_app(self) -> None:
        """TODO: Add docstring."""
        handler = AsyncSocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
        await handler.start_async()

    def run(self) -> None:
        """TODO: Add docstring."""
        with ProcessPoolExecutor() as pool:
            self.pool = pool
            asyncio.run(self._slack_app())

    def fix_md_for_slack(self, md_text: str) -> str:
        """TODO: Add docstring."""
        # Convert **bold** to *bold* (Slack syntax)
        slack_text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", md_text)

        # Convert *italic* to _italic_ (Slack syntax)
        slack_text = re.sub(r"\*(.*?)\*", r"_\1_", slack_text)

        # Convert [text](link) to <link|text> (Slack link syntax)
        slack_text = re.sub(r"\[(.*?)\]\((.*?)\)", r"<\2|\1>", slack_text)

        return slack_text

    async def message_hello(self, message: Any, ack: Any) -> None:
        """TODO: Add docstring.

        Change the method param types and return types.
        """
        await ack()

        if thread_ts := message.get("thread_ts"):
            text = message["text"]
            future = self.pool.submit(self.assistant.handle_reply, thread_ts, text)
            response = await self.await_future(future)
            LOGGER.info("response: %s", response)

            r = await app.client.chat_postMessage(
                channel=os.getenv("SLACK_CHANNEL_ID"),
                thread_ts=thread_ts,
                blocks=[
                    {
                        "type": "context",
                        "elements": [
                            {
                                "type": "mrkdwn",
                                "text": self.fix_md_for_slack(response),
                            },
                        ],
                    },
                ],
                unfurl_links=False,
                unfurl_media=False,
            )
            r.validate()

        match message["text"]:
            case str(value) if "fetch" in value:
                future = self.pool.submit(self.assistant.fetch_emails)
                found = await self.await_future(future)
                LOGGER.info("%s new emails found", found)

            case str(value) if "handle_one" in value:
                future = self.pool.submit(self.assistant.handle_one)
                result = await self.await_future(future)

                time = datetime.fromisoformat(result["time_received"])

                r = await app.client.chat_postMessage(
                    channel=os.getenv("SLACK_CHANNEL_ID"),
                    text=f"Handling `{result['id']}`...",
                    unfurl_links=False,
                    unfurl_media=False,
                )
                r.validate()
                ts = r.get("ts")

                r = await app.client.chat_update(
                    channel=os.getenv("SLACK_CHANNEL_ID"),
                    ts=ts,
                    blocks=[
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"`From:` {result['author']}",
                                },
                            ],
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"`When:` <https://mail.google.com/mail/u/0/#inbox/{result['id']}|{time}>",
                                },
                            ],
                        },
                        {"type": "divider"},
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"{result['summary']}",
                                },
                            ],
                        },
                        {
                            "type": "context",
                            "elements": [
                                {
                                    "type": "mrkdwn",
                                    "text": f"{result['action']}",
                                },
                            ],
                        },
                    ],
                )
                r.validate()

                db = DB()
                item = db.session.query(Item).where(Item.id == result["id"]).one()
                item.slack_channel = "C01CAH729TK"
                item.slack_thread = r.get("ts")
                db.session.commit()
        logger_msg = "\n" + pformat(message)
        LOGGER.info(logger_msg)


if __name__ == "__main__":
    Server().run()

# https://mail.google.com/mail/u/0/#inbox/19245a9bd60a75f6
