"""TODO: Add docstring."""

import enum

from openai import OpenAI
from openai.types.chat import ChatCompletion
from pydantic import BaseModel


class Role(enum.StrEnum):
    """TODO: Add docstring."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Line(BaseModel):
    """TODO: Add docstring."""

    role: Role
    content: str


class GPT:
    """TODO: Add docstring."""

    def __init__(self) -> None:
        """TODO: Add docstring."""
        self.client = OpenAI()

    def complete(self, log: list[Line]) -> ChatCompletion:
        """TODO: Add docstring."""
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": x.role, "content": x.content} for x in log],
        )
