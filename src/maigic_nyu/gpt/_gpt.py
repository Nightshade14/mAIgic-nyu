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
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "create_card",
                    "description": "Create a Trello card in the appropriate list based on its type.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "card_type": {
                                "type": "string",
                                "description": "The type of the card (e.g., 'meeting', 'event', 'general').",
                            },
                            "card_name": {
                                "type": "string",
                                "description": "The name of the card.",
                            },
                            "card_desc": {
                                "type": "string",
                                "description": "The description of the card.",
                            },
                            "due_date": {
                                "type": "string",
                                "format": "date-time",
                                "description": "The due date for the card in ISO 8601 format (e.g., '2024-11-20T12:00:00Z'). Optional.",
                                "nullable": True,
                            },
                        },
                        "required": ["card_type", "card_name", "card_desc"],
                    },
                },
            },
        ]

    def complete(self, log: list[Line]) -> ChatCompletion:
        """TODO: Add docstring."""
        return self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": x.role, "content": x.content} for x in log],
        )
