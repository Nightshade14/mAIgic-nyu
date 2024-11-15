"""TODO: Add docstring."""

import os

from slack_sdk import WebClient


class Slack:
    """TODO: Add docstring."""

    def __init__(self) -> None:
        """TODO: Add docstring."""
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    def send(self, thread: str | None, text: str) -> None:
        """TODO: Add docstring."""
        r = self.client.chat_postMessage(
            channel=os.getenc("SLACK_CHANNEL_ID"),
            thread=thread,
            text=text,
        )
        r.validate()
        return r
