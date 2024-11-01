import json
from pprint import pformat
from typing import Any
from src.db.models import DB, Chat, Item, ItemType
from src.gmail.client import Gmail
from src.gmail.models import GMailMessage
import logging

from src.gpt.gpt import GPT, Line, Role
from pydantic import BaseModel

LOGGER = logging.getLogger(__file__)


GMAIL_PRIMER = Line(
    role=Role.SYSTEM,
    # FIXME: this content needs to be tailored to the custome
    content="""
        I am Kamen Yotov.
        My emails are kamen@yotov.org, kyotov@gmail.com, ky12@nyu.edu.
        
        When I first receive an email, I want you to analyze it respond with the analysis in json as follows:

        * "author"
        * "time_received" in iso format
        * "categories"
            ** "urgent": bool
            ** "important": bool
            ** "spam": bool
        * "summary" : summary of the content
        * "action": proposed next action

        Then answer my follow up questions in markdown supported by slack api.
    """,
)


class ItemKey(BaseModel):
    type: ItemType
    id: str

    @classmethod
    def from_item(cls, item: Item) -> "ItemKey":
        return ItemKey(type=item.type, id=item.id)


class Conversation:
    def __init__(self, db: DB, gpt: GPT, item_key: ItemKey) -> None:
        self.db = db
        self.gpt = gpt
        self.item_key = item_key

        self.item = (
            db.session.query(Item)
            .where((Item.type == item_key.type) & (Item.id == item_key.id))
            .one()
        )

        self.thread = list(
            db.session.query(Chat)
            .where((Chat.type == item_key.type) & (Chat.id == item_key.id))
            .order_by(Chat.seq)
            .all()
        )

    def primer_lines(self) -> list[Line]:
        return [
            GMAIL_PRIMER,
            Line(role=Role.USER, content=self.item.content),
        ]

    def handle_user_reply(self, message: str = "") -> str:
        lines = self.primer_lines() + [
            Line(role=x.role, content=x.content) for x in self.thread
        ]

        if len(lines) == 2:  # this conversation has not started yet!
            assert message == ""  # there is no message by user yet!
        else:
            assert len(lines) >= 3, lines  # there should be at least 1 reply ...
            assert lines[-1].role == Role.ASSISTANT  # ... by the assistant

            assert message
            lines.append(Line(role=Role.USER, content=message))

        r = self.gpt.complete(lines)

        # TODO: this is where we need to differentiate if it is a tool/function call...
        #       for now assert it is not!
        assert len(r.choices) == 1
        choice = r.choices[0]
        assert choice.finish_reason == "stop"
        result = choice.message.content
        assert result

        self.db.session.add(
            Chat(
                type=self.item.type,
                id=self.item.id,
                role=Role.USER,
                content=message,
            )
        )
        self.db.session.add(
            Chat(
                type=self.item.type,
                id=self.item.id,
                role=Role.ASSISTANT,
                content=result,
            )
        )
        self.db.session.commit()

        return result


class Assistant:
    def __init__(self) -> None:
        # self.db = DB()
        # self.gpt = GPT()
        pass

    def fetch_emails(self) -> int:
        try:
            gmail = Gmail()
            db = DB()
            new_count = 0
            # TODO(kamen): figure out how to query for new emails only?
            #   maybe based on date of the last email we know about?
            #   just ask for emails that are newer than that date?
            for message in gmail.query():
                if (
                    found := db.session.query(Item)
                    .where((Item.type == ItemType.gmail) & (Item.id == message["id"]))
                    .first()
                ):
                    LOGGER.debug("skipping %s already in database", found.id)
                else:
                    mm = gmail.get_message(message["id"])
                    m = GMailMessage(mm)
                    db.session.add(
                        Item(type=ItemType.gmail, id=mm["id"], content=m.as_md())
                    )
                    db.session.commit()
                    LOGGER.debug("added %s to database", mm["id"])
                    new_count += 1
            return new_count
        except Exception:
            LOGGER.exception("fetch_emails failed")
            raise

    def handle_one(self) -> dict[str, Any]:
        try:
            db = DB()
            gpt = GPT()

            if (
                new_item := db.session.query(Item)
                .where(Item.slack_thread.is_(None))
                .first()
            ):
                convo = Conversation(db, gpt, ItemKey.from_item(new_item))

                LOGGER.info("handling %s", new_item.id)

                result = convo.handle_user_reply()
                result = result.removeprefix("```json").removesuffix("```")
                result = json.loads(result)
                result["id"] = new_item.id

                LOGGER.info(pformat(result))
                return result
        except:
            LOGGER.exception("")
            raise

    def handle_reply(self, thread_ts: str, reply: str) -> str:
        try:
            db = DB()
            gpt = GPT()

            if (
                item := db.session.query(Item)
                .where(Item.slack_thread == thread_ts)
                .first()
            ):
                convo = Conversation(db, gpt, ItemKey.from_item(item))

                LOGGER.info("handling reply on %s for %s", thread_ts, item.id)
                result = convo.handle_user_reply(reply)
                LOGGER.info(pformat(result))
                return result
            else:
                raise RuntimeError(f"item not found for {thread_ts}")
        except Exception as error_msg:
            LOGGER.exception(str(error_msg))


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    a = Assistant()
    a.fetch_emails()
    a.handle_one()
