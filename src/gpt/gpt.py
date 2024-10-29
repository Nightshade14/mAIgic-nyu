from openai import OpenAI
from pydantic import BaseModel
import enum
from openai.types.chat import ChatCompletion
import logging

LOGGER = logging.getLogger(__file__)


class Role(enum.StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Line(BaseModel):
    role: Role
    content: str
    name: str | None = None  # Added for function calls


class GPT:
    def __init__(self) -> None:
        self.client = OpenAI()
        # Define available functions
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "save_summary",
                    "description": "Save content to a local file in the summaries directory",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The text content to save",
                            },
                            "filename": {
                                "type": "string",
                                "description": "Optional custom filename",
                            },
                        },
                        "required": ["content"],
                    },
                },
            }
        ]

    def complete(self, log: list[Line]) -> ChatCompletion:
        try:
            # debug
            LOGGER.info("Sending request to GPT with %d messages", len(log))

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": x.role, "content": x.content, "name": x.name}
                    for x in log
                    if x.content
                ],
                tools=self.tools,
                tool_choice="auto",
            )

            # debug
            LOGGER.info("Received response from GPT")
            return response
        except Exception as e:
            # debug
            LOGGER.error("Error in GPT completion: %s", str(e))
            raise
