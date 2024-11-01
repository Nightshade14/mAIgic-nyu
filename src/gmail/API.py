from typing import Optional, Generator
from datetime import datetime
from .client import Gmail

# Create a single instance of Gmail
_gmail = Gmail()


def query(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    max_results: int = 10000,
) -> Generator[dict, None, None]:
    """Query Gmail messages with filters."""
    return _gmail.query(start_date, end_date, max_results)


def get_message(message_id: str) -> dict:
    """Fetch a specific email message by ID."""
    return _gmail.get_message(message_id)


def get_labels() -> list[dict]:
    """Fetch all labels in the user's mailbox."""
    return _gmail.get_labels()


def search(query: str, max_results: int = 100) -> Generator[dict, None, None]:
    """Search emails using Gmail's query syntax."""
    return _gmail.search(query, max_results)


# Export only the public functions
__all__ = ["query", "get_message", "get_labels", "search"]
