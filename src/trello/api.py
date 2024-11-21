from datetime import datetime
from typing import Any

from .trello_manager import TrelloCard, TrelloChecklist, TrelloManager

# Instantiate a single object of TelloManager
tm = TrelloManager()

# TrelloManager comes with the following methods:
# 1. create_card: Creates a new Trello card in a specified list with optional
# description and due date.
def create_card(self, list_id: str, name: str, desc: str = "",
                   due_date: datetime | None = None) -> TrelloCard:
    """Create a new card with enhanced features."""
    return tm.create_card(list_id, name, desc, due_date)

# 2. add_attachment: Adds an attachment to a specified Trello card.
def add_attachment(self,
                       card_id: str,
                       url: str,
                       name: str | None = None) -> bool:
    """Add an attachment to a card."""
    return tm.add_attachment(card_id, url, name)

# 3. create_checklist: Creates a new checklist on a specified Trello card.
def create_checklist(self, card_id: str, name: str) -> TrelloChecklist:
    """Create a new checklist on a card."""
    return tm.create_checklist(card_id, name)

# 4. add_checklist_item: Adds an item to a specified checklist.
def add_checklist_item(self,
                        checklist_id: str,
                        name: str,
                        checked: bool = False) -> dict[str, Any]:
    """Add an item to a checklist."""
    return tm.add_checklist_item(checklist_id, name, checked)

# 5. update_card_due_date: Updates or removes the due date of a specified Trello card.
def update_card_due_date(self, card_id: str, due_date: datetime | None) -> bool:
    """Update or remove a card's due date."""
    return tm.update_card_due_date(card_id, due_date)

# 6. search_cards: Searches for cards based on a query, with an optional filter
# for a specific board.
def search_cards(self,
                query: str,
                board_id: str | None = None) -> list[TrelloCard]:
    """Search for cards with optional board filter."""
    return tm.search_cards(query, board_id)

# 7. get_full_board_info: Retrieves the full ID of a Trello board using its short ID.
def get_full_board_info(self, short_board_id: str) -> str:
    """Get full board information from Trello.
    Args:
        short_board_id (str): The short ID of the Trello board.
    Returns:
        str: The full board ID.
    """
    return tm.get_full_board_info(short_board_id)

# 8. get_lists: Retrieves all lists in a specified Trello board.
def get_lists(self, board_id: str) -> list:
    """Get all lists in the specified Trello board.
    Args:
        board_id (str): The full ID of the Trello board.
    Returns:
        list: A list of list IDs.
    """
    return tm.get_lists(board_id)

# 9. add_comment_to_card: Adds a comment to a specified Trello card.
def add_comment_to_card(self, card_id: str, comment: str) -> bool:
    """Add a comment to an existing card.
    Args:
        card_id (str): The ID of the card.
        comment (str): The comment text to add.
    Returns:
        bool: True if comment was added successfully, False otherwise.
    """
    return tm.add_comment_to_card(card_id, comment)

# 10. add_label_to_card: Adds a label to a specified Trello card with a
# given name and color.
def add_label_to_card(self,
                        card_id: str,
                        label_name: str,
                        color: str = "blue") -> bool:
    """Add a label to a card.
    Args:
        card_id (str): The ID of the card.
        label_name (str): The name of the label.
        color (str): The color of the label (default: "blue").
    Returns:
        bool: True if label was added successfully, False otherwise.
    """
    return tm.add_label_to_card(card_id, label_name, color)

# 11. move_card: Moves a specified Trello card to a different list.
def move_card(self, card_id: str, target_list_id: str) -> bool:
    """Move a card to a different list.
    Args:
        card_id (str): The ID of the card to move.
        target_list_id (str): The ID of the destination list.
    Returns:
        bool: True if card was moved successfully, False otherwise.
    """
    return tm.move_card(card_id, target_list_id)

# 12. archive_card: Archives (closes) a specified Trello card.
def archive_card(self, card_id: str) -> bool:
    """Archive (close) a card.
    Args:
        card_id (str): The ID of the card to archive.
    Returns:
        bool: True if card was archived successfully, False otherwise.
    """
    return tm.archive_card(card_id)

# 13. get_list_name: Retrieves the name of a specified list using its ID.
def get_list_name(self, list_id: str) -> str:
    """Get the list name of a specific list id in the specific board.
    Args:
        list_id (str): the id of the specific list.
    Returns:
        str: the name of the specific list.
    """
    return tm.get_list_name(list_id)

# 14. create_a_list: Creates a new list on a specified Trello board and returns its ID.
def create_a_list(self, list_name: str, id_board: str) -> str:
    """Create a new list on the specified Trello board.
    Args:
        list_name (str): The name of the new list.
        id_board (str): The ID of the board where the list will be created.
    Returns:
        str: The ID of the created list, or an empty string if creation failed.
    """
    return tm.create_a_list(list_name, id_board)

# 15. validate_board_access: Validates whether the current API credentials have
# access to a specified Trello board.
def validate_board_access(self, board_id: str) -> bool:
    """Validate that the current API credentials have access to the board."""
    return tm.validate_board_access(board_id)

# Export all the functions
__all__ = ["create_card", "add_attachment", "create_checklist", "add_checklist_item",
           "search_cards", "get_full_board_info", "get_lists", "add_comment_to_card",
           "add_label_to_card", "update_card_due_date","move_card", "archive_card",
           "get_list_name", "create_a_list", "validate_board_access"]
