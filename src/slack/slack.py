import os

from slack_sdk import WebClient


class Slack:
    def __init__(self) -> None:
        # replaced client with self.client as client was not used anywhere
        self.client = WebClient(token=os.getenv("SLACK_BOT_TOKEN"))

    def send(self, thread: str | None, text: str) -> None:
        r = self.client.chat_postMessage(
            channel=os.getenc("SLACK_CHANNEL_ID"),
            thread=thread,
            text=text,
        )
        r.validate()
        return r
