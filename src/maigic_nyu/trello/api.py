"""API module that exposes Trello functionality to users."""
from datetime import datetime
from typing import Any

from src.maigic_nyu.trello._trello_manager import (  # Fix the import path
    TrelloCard,
    TrelloChecklist,
    TrelloManager,
    _TrelloAPIError,
    _TrelloError,
    _TrelloRateLimitError,
)

__all__ = [
    "TrelloAPIError",
    "TrelloCard",
    "TrelloChecklist",
    "TrelloError",
    "TrelloRateLimitError",
    "add_attachment",
    "add_checklist_item",
    "add_comment",
    "add_label",
    "archive_card",
    "create_card",
    "create_checklist",
    "create_list",
    "get_board_lists",
    "get_list_name",
    "move_card",
    "search_cards",
    "update_card_due_date",
]

# Re-export exceptions with public names
TrelloError = _TrelloError
TrelloAPIError = _TrelloAPIError
TrelloRateLimitError = _TrelloRateLimitError

# Global TrelloManager instance
_trello = None

def _get_trello() -> TrelloManager:
    """Get or create the global TrelloManager instance."""
    global _trello
    if _trello is None:
        _trello = TrelloManager()
    return _trello

def create_card(
    list_id: str,
    name: str,
    description: str = "",
    due_date: datetime | None = None
) -> TrelloCard:
    """Create a new Trello card.

    Args:
        list_id: ID of the list to create the card in
        name: Name of the card
        description: Card description (optional)
        due_date: Due date for the card (optional)

    Returns:
        TrelloCard object representing the created card

    """
    return _get_trello().create_card(list_id, name, description, due_date)

def add_attachment(
    card_id: str,
    url: str,
    name: str | None = None
) -> bool:
    """Add an attachment to a card.

    Args:
        card_id: ID of the card
        url: URL of the attachment
        name: Display name for the attachment (optional)

    Returns:
        True if attachment was added successfully

    """
    return _get_trello().add_attachment(card_id, url, name)

def create_checklist(card_id: str, name: str) -> TrelloChecklist:
    """Create a new checklist on a card.

    Args:
        card_id: ID of the card
        name: Name of the checklist

    Returns:
        TrelloChecklist object representing the created checklist

    """
    return _get_trello().create_checklist(card_id, name)

def add_checklist_item(
    checklist_id: str,
    name: str,
    *, # Make checked keyword-only
    checked: bool = False
) -> dict[str, Any]:
    """Add an item to a checklist.

    Args:
        checklist_id: ID of the checklist
        name: Name of the checklist item
        checked: Whether the item should be checked by default

    Returns:
        Dictionary containing the created checklist item details

    """
    return _get_trello().add_checklist_item(
        checklist_id=checklist_id,
        name=name,
        checked=checked
    )

def update_card_due_date(
    card_id: str,
    due_date: datetime | None
) -> bool:
    """Update or remove a card's due date.

    Args:
        card_id: ID of the card
        due_date: New due date, or None to remove the due date

    Returns:
        True if the due date was updated successfully

    """
    return _get_trello().update_card_due_date(card_id, due_date)

def search_cards(
    query: str,
    board_id: str | None = None
) -> list[TrelloCard]:
    """Search for cards with optional board filter.

    Args:
        query: Search query string
        board_id: Optional board ID to limit search scope

    Returns:
        List of TrelloCard objects matching the search criteria

    """
    return _get_trello().search_cards(query, board_id)

def get_board_lists(board_id: str) -> list[str]:
    """Get all lists in a board.

    Args:
        board_id: ID of the board

    Returns:
        List of list IDs in the board

    """
    return _get_trello().get_lists(board_id)

def add_comment(card_id: str, comment: str) -> bool:
    """Add a comment to a card.

    Args:
        card_id: ID of the card
        comment: Comment text

    Returns:
        True if comment was added successfully

    """
    return _get_trello().add_comment_to_card(card_id, comment)

def add_label(
    card_id: str,
    label_name: str,
    color: str = "blue"
) -> bool:
    """Add a label to a card.

    Args:
        card_id: ID of the card
        label_name: Name of the label
        color: Color of the label (default: "blue")

    Returns:
        True if label was added successfully

    """
    return _get_trello().add_label_to_card(card_id, label_name, color)

def move_card(card_id: str, target_list_id: str) -> bool:
    """Move a card to a different list.

    Args:
        card_id: ID of the card to move
        target_list_id: ID of the destination list

    Returns:
        True if card was moved successfully

    """
    return _get_trello().move_card(card_id, target_list_id)

def archive_card(card_id: str) -> bool:
    """Archive (close) a card.

    Args:
        card_id: ID of the card to archive

    Returns:
        True if card was archived successfully

    """
    return _get_trello().archive_card(card_id)

def get_list_name(list_id: str) -> str:
    """Get the name of a list.

    Args:
        list_id: ID of the list

    Returns:
        Name of the list, or empty string if not found

    """
    return _get_trello().get_list_name(list_id)

def create_list(list_name: str, board_id: str) -> str:
    """Create a new list on a board.

    Args:
        list_name: Name of the new list
        board_id: ID of the board

    Returns:
        ID of the created list, or empty string if creation failed

    """
    return _get_trello().create_a_list(list_name, board_id)
