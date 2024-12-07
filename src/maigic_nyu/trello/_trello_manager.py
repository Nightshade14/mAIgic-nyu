import logging
import os
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Optional

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HTTP_OK = 200
MAX_RETRIES = 3
RETRY_DELAY = 1
RATE_LIMIT_STATUS = 429

class _TrelloError(Exception):
    """Base exception for Trello-related errors."""

class _TrelloAPIError(_TrelloError):
    """Exception raised for errors in the API response."""

class _TrelloRateLimitError(_TrelloError):
    """Exception raised when hitting Trello's rate limits."""

@dataclass
class TrelloCard:
    """Represents a Trello card with its attributes."""

    id: str
    name: str
    desc: str
    url: str
    board_id: str
    list_id: str
    due_date: datetime | None = None
    members: list[str] = field(default_factory=list)
    labels: list[dict[str, str]] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize default values for members and labels."""
        self.members = self.members or []
        self.labels = self.labels or []

@dataclass
class TrelloChecklist:
    """Represents a Trello checklist."""

    id: str
    name: str
    items: list[dict[str, Any]]


class TrelloManager:
    """A class to interact with the Trello API using Singleton Pattern."""

    _instance: ClassVar[Optional["TrelloManager"]] = None
    BASE_URL: ClassVar[str] = "https://api.trello.com/1"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        load_dotenv()
        self.api_key = os.getenv("TRELLO_API_KEY")
        self.token = os.getenv("TRELLO_OAUTH_TOKEN")

        if not self.api_key or not self.token:
            msg = "Missing Trello API credentials"
            raise _TrelloError(msg)

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        retries: int = MAX_RETRIES,
    ) -> dict[str, Any]:
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        params = params or {}
        params.update({"key": self.api_key, "token": self.token})

        for attempt in range(retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    timeout=10,
                )

                if response.status_code == RATE_LIMIT_STATUS:
                    retry_after = int(response.headers.get("Retry-After", RETRY_DELAY))
                    if attempt < retries - 1:
                        time.sleep(retry_after)
                        continue
                    msg = f"Rate limit exceeded. Retry after {retry_after} seconds"
                    raise _TrelloRateLimitError(msg)

                response.raise_for_status()
                return response.json()

            except requests.exceptions.RequestException as e:
                if attempt == retries - 1:
                    msg = f"API request failed: {e!s}"
                    raise _TrelloAPIError(msg) from e
                time.sleep(RETRY_DELAY)

        msg = "Max retries exceeded"
        raise _TrelloAPIError(msg)

    def create_card(self, list_id: str, name: str, desc: str = "", due_date: datetime | None = None) -> TrelloCard:
        params = {"idList": list_id, "name": name, "desc": desc}
        if due_date:
            params["due"] = due_date.isoformat()
        data = self._make_request("post", "/cards", params=params)
        return TrelloCard(
            id=data["id"],
            name=data["name"],
            desc=data["desc"],
            url=data["shortUrl"],
            board_id=data["idBoard"],
            list_id=data["idList"],
            due_date=datetime.fromisoformat(data["due"]) if data.get("due") else None,
            members=data.get("idMembers", []),
            labels=data.get("labels", []),
        )

    def add_attachment(self, card_id: str, url: str, name: str | None = None) -> bool:
        """Add an attachment to a card."""
        params = {"url": url}
        if name:
            params["name"] = name
        self._make_request("post", f"/cards/{card_id}/attachments", params=params)
        return True

    def create_checklist(self, card_id: str, name: str) -> TrelloChecklist:
        """Create a new checklist on a card."""
        data = self._make_request("post", f"/cards/{card_id}/checklists", params={"name": name})
        return TrelloChecklist(
            id=data["id"],
            name=data["name"],
            items=[],
        )

    def add_checklist_item(
        self,
        checklist_id: str,
        name: str,
        *,
        checked: bool = False
    ) -> dict[str, Any]:
        """Add an item to a checklist.

        Args:
            checklist_id: ID of the checklist
            name: Name of the item
            checked: Whether the item is checked (keyword-only argument)

        Returns:
            Dictionary containing the created checklist item details

        """
        return self._make_request(
            "post",
            f"/checklists/{checklist_id}/checkItems",
            params={"name": name, "checked": str(checked).lower()}
        )

    def update_card_due_date(self, card_id: str, due_date: datetime | None) -> bool:
        """Update or remove a card's due date."""
        params = {"due": due_date.isoformat() if due_date else None}
        self._make_request("put", f"/cards/{card_id}", params=params)
        return True

    def search_cards(self, query: str, board_id: str | None = None) -> list[TrelloCard]:
        """Search for cards with optional board filter."""
        params = {"query": query}
        if board_id:
            params["idBoards"] = board_id

        data = self._make_request("get", "/search", params=params)
        return [
            TrelloCard(
                id=card["id"],
                name=card["name"],
                desc=card["desc"],
                url=card["shortUrl"],
                board_id=card["idBoard"],
                list_id=card["idList"],
                due_date=datetime.fromisoformat(card["due"]) if card.get("due") else None,
                members=card.get("idMembers", []),
                labels=card.get("labels", []),
            )
            for card in data.get("cards", [])
        ]

    def get_full_board_info(self, short_board_id: str) -> str:
        """Get full board information from Trello.

        Args:
            short_board_id (str): The short ID of the Trello board.

        Returns:
            str: The full board ID.

        """
        url = f"{self.BASE_URL}/boards/{short_board_id}"
        query = {
            "key": self.api_key,
            "token": self.token,
        }
        response = requests.get(url, params=query, timeout=10)

        if response.status_code == HTTP_OK:
            board_info = response.json()
            return board_info["id"]
        return ""

    def get_lists(self, board_id: str) -> list:
        """Get all lists in the specified Trello board.

        Args:
            board_id (str): The full ID of the Trello board.

        Returns:
            list: A list of list IDs.

        """
        url = f"{self.BASE_URL}/boards/{board_id}/lists"
        query = {
            "key": self.api_key,
            "token": self.token,
        }
        response = requests.get(url, params=query, timeout=10)

        list_id = []
        if response.status_code == HTTP_OK:
            lists = response.json()
            list_id = [lst["id"] for lst in lists]

        return list_id

    def add_comment_to_card(self, card_id: str, comment: str) -> bool:
        """Add a comment to an existing card.

        Args:
            card_id (str): The ID of the card.
            comment (str): The comment text to add.

        Returns:
            bool: True if comment was added successfully, False otherwise.

        """
        url = f"{self.BASE_URL}/cards/{card_id}/actions/comments"
        query = {
            "key": self.api_key,
            "token": self.token,
            "text": comment,
        }
        response = requests.post(url, params=query, timeout=10)
        return response.status_code == HTTP_OK

    def add_label_to_card(self, card_id: str, label_name: str, color: str = "blue") -> bool:
        """Add a label to a card.

        Args:
            card_id (str): The ID of the card.
            label_name (str): The name of the label.
            color (str): The color of the label (default: "blue").

        Returns:
            bool: True if label was added successfully, False otherwise.

        """
        url = f"{self.BASE_URL}/cards/{card_id}/labels"
        query = {
            "key": self.api_key,
            "token": self.token,
            "name": label_name,
            "color": color,
        }
        response = requests.post(url, params=query, timeout=10)
        return response.status_code == HTTP_OK

    def move_card(self, card_id: str, target_list_id: str) -> bool:
        """Move a card to a different list.

        Args:
            card_id (str): The ID of the card to move.
            target_list_id (str): The ID of the destination list.

        Returns:
            bool: True if card was moved successfully, False otherwise.

        """
        url = f"{self.BASE_URL}/cards/{card_id}"
        query = {
            "key": self.api_key,
            "token": self.token,
            "idList": target_list_id,
        }
        response = requests.put(url, params=query, timeout=10)
        return response.status_code == HTTP_OK

    def archive_card(self, card_id: str) -> bool:
        """Archive (close) a card.

        Args:
            card_id (str): The ID of the card to archive.

        Returns:
            bool: True if card was archived successfully, False otherwise.

        """
        url = f"{self.BASE_URL}/cards/{card_id}"
        query = {
            "key": self.api_key,
            "token": self.token,
            "closed": "true",
        }
        response = requests.put(url, params=query, timeout=10)
        return response.status_code == HTTP_OK

    def get_list_name(self, list_id: str) -> str:
        """Get the list name of a specific list id in the specific board.

        Args:
            list_id (str): the id of the specific list.

        Returns:
            str: the name of the specific list.

        """
        url = f"{self.BASE_URL}/lists/{list_id}"
        query = {
            "key": self.api_key,
            "token": self.token,
        }
        response = requests.get(url, params=query, timeout=10)

        if response.status_code == HTTP_OK:
            list_info = response.json()
            return list_info.get("name", "No name found")

        return ""

    def create_a_list(self, list_name: str, id_board: str) -> str:
        """Create a new list on the specified Trello board.

        Args:
            list_name (str): The name of the new list.
            id_board (str): The ID of the board where the list will be created.

        Returns:
            str: The ID of the created list, or an empty string if creation failed.

        """
        url = f"{self.BASE_URL}/lists"
        query = {
            "idBoard": id_board,
            "name": list_name,
            "key": self.api_key,
            "token": self.token,
        }

        response = requests.post(url, params=query, timeout=10)
        if response.status_code == HTTP_OK:
            logger.info("List creation succeed!")
            return response.json().get("id")

        logger.info("List creation failed")
        return ""

    def validate_board_access(self, board_id: str) -> bool:
        """Validate that the current API credentials have access to the board."""
        try:
            self._make_request("get", f"/boards/{board_id}")
        except _TrelloAPIError:
            return False
        else:
            return True
