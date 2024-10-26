from openai import OpenAI
from pydantic import BaseModel
import enum
from openai.types.chat import ChatCompletion


class Role(enum.StrEnum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    FUNCTION = "function"


class Line(BaseModel):
    role: Role
    content: str


class GPT:
    def __init__(self) -> None:
        self.client = OpenAI()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "save_summary",
                    "description": "Save content to a local file",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "content": {
                                "type": "string",
                                "description": "The content to save"
                            },
                            "filename": {
                                "type": "string",
                                "description": "Optional filename (will generate if not provided)",
                            }
                        },
                        "required": ["content"]
                    }
                }
            }
        ]

    def complete(self, log: list[Line]) -> ChatCompletion:
        return self.client.chat.completions.create(
            # model="gpt-4",
            model="gpt-4o-mini",
            messages=[{"role": x.role, "content": x.content} for x in log],
            tools=self.tools,
            tool_choice="auto"
        )
