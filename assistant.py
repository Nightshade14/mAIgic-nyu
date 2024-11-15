"""TODO: Add docstring."""

import json
import logging
from pathlib import Path
from pprint import pformat
from typing import Any, NoReturn

import yaml
from pydantic import BaseModel

from maigic_nyu.db.api import DB, Chat, Item, ItemType
from maigic_nyu.gmail.api import Gmail, GMailMessage
from maigic_nyu.gpt.api import GPT, Line, Role

LOGGER = logging.getLogger(__name__)


system_prompt = None
prompt_path = "./llm_prompts/prompts.yaml"
with Path(prompt_path).open(mode="r", encoding="utf-8") as fp:
    system_prompt = yaml.safe_load(fp)["system_prompt"]

GMAIL_PRIMER = Line(
    role=Role.SYSTEM,
    # TODO: this content needs to be tailored to the customer
    content=system_prompt,
)


class ItemKey(BaseModel):
    """TODO: Add docstring."""

    type: ItemType
    id: str

    @classmethod
    def from_item(cls, item: Item) -> "ItemKey":
        """TODO: Add docstring."""
        return ItemKey(type=item.type, id=item.id)


class Conversation:
    """TODO: Add docstring."""

    def __init__(self, db: DB, gpt: GPT, item_key: ItemKey) -> None:
        """TODO: Add docstring."""
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
        """TODO: Add docstring."""
        return [
            GMAIL_PRIMER,
            Line(role=Role.USER, content=self.item.content),
        ]

    def handle_user_reply(self, message: str = "") -> str:
        """TODO: Add docstring."""
        num_of_lines_conv_not_started = 2
        num_of_lines_atleast_one_reply = 3

        lines = self.primer_lines() + [
            Line(role=x.role, content=x.content) for x in self.thread
        ]

        # this conversation has not started yet!
        if len(lines) == num_of_lines_conv_not_started:
            assert message == ""  # there is no message by user yet!
        else:
            # there should be at least 1 reply by the assistant
            assert len(lines) >= num_of_lines_atleast_one_reply, lines
            assert lines[-1].role == Role.ASSISTANT

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
    """TODO: Add docstring."""

    def __init__(self) -> None:
        """TODO: Add docstring.

        TODO: Replace gmail, db and gpt in the codes with the self. versions
        and see if it works. All 3: db, gpt, gmail.
        """

    def fetch_emails(self) -> int:
        """TODO: Add docstring."""
        try:
            gmail = Gmail()
            db = DB()
            new_count = 0
            # TODO(kamen): figure out how to query for new emails only?
            #   maybe based on date of the last email we know about?
            #   just ask for emails that are newer than that date?
            for message in gmail.query():
                if (
                    found := self.db.session.query(Item)
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
                    self.db.session.commit()
                    LOGGER.debug("added %s to database", mm["id"])
                    new_count += 1
        except Exception:
            LOGGER.exception("fetch_emails failed")
            raise
        else:
            return new_count

    def handle_one(self) -> dict[str, Any]:
        """TODO: Add docstring."""
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

    def raise_runtime_error(self, msg: str = "Runtime error raised") -> NoReturn:
        """Raise Runtime error.

        This func raises a runtime error with a custom message or with the default one.
        It is used to abstract away raising exceptions directly in try block.
        """
        raise RuntimeError(msg)

    def handle_reply(self, thread_ts: str, reply: str) -> str:
        """TODO: Add docstring."""
        run_time_error_msg = f"item not found for {thread_ts}"
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

            self.raise_runtime_error(run_time_error_msg)
        except RuntimeError:
            LOGGER.exception(run_time_error_msg)

        except Exception:
            LOGGER.exception("Exception")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    a = Assistant()
    a.fetch_emails()
    a.handle_one()
