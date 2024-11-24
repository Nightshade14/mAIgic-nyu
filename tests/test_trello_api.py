"""Tests for the Trello API module."""
import os
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.maigic_nyu.trello import api
from src.maigic_nyu.trello._trello_manager import TrelloManager
from src.maigic_nyu.trello.api import (
    TrelloCard,
    TrelloChecklist,
    add_attachment,
    add_checklist_item,
    add_comment,
    add_label,
    archive_card,
    create_card,
    create_checklist,
    create_list,
    get_board_lists,
    get_list_name,
    move_card,
    search_cards,
    update_card_due_date,
)

# We need to access private members for testing, so disable the warning
# ruff: noqa: SLF001

@pytest.fixture(autouse=True)
def mock_env_vars() -> Generator[None, None, None]:
    """Fixture to mock environment variables."""
    with patch.dict(os.environ, {
        "TRELLO_API_KEY": "dummy_api_key",
        "TRELLO_OAUTH_TOKEN": "dummy_token"
    }):
        yield

@pytest.fixture
def mock_trello_manager() -> Generator[MagicMock, None, None]:
    """Fixture to provide a mocked TrelloManager instance."""
    with patch("src.maigic_nyu.trello.api.TrelloManager") as mock:
        instance = mock.return_value
        original_trello = api._trello
        api._trello = instance
        yield instance
        api._trello = original_trello

@pytest.fixture
def sample_card() -> TrelloCard:
    """Fixture to provide a sample TrelloCard instance."""
    return TrelloCard(
        id="card123",
        name="Test Card",
        desc="Test Description",
        url="https://trello.com/c/abc123",
        board_id="board123",
        list_id="list123",
        due_date=datetime(2024, 12, 31, tzinfo=UTC),
        members=["member1"],
        labels=[{"name": "Priority", "color": "red"}]
    )


def test_get_trello_creates_instance() -> None:
    """Test that _get_trello creates a new instance when none exists."""
    patches = [
        patch("src.maigic_nyu.trello.api.TrelloManager"),
    ]

    for p in patches:
        with p as mock_class:
            # Reset for each attempt
            api._trello = None

            # Get a new instance

            result = api._get_trello()
            if mock_class.call_count > 0:
                mock_class.assert_called_once()
                assert result == mock_class.return_value
                return

    pytest.fail("Could not find correct patch path for TrelloManager")

def test_get_trello_reuses_instance() -> None:
    """Test that _get_trello reuses an existing instance."""
    # Create and store a mock instance
    mock_instance = MagicMock(spec=TrelloManager)
    api._trello = mock_instance

    # Get the instance through _get_trello
    result = api._get_trello()

    # Verify it's the same instance we stored
    assert result is mock_instance

def test_singleton_pattern() -> None:
    """Test the complete singleton pattern."""
    patches = [
        patch("src.maigic_nyu.trello.api.TrelloManager")
    ]

    for p in patches:
        with p as mock_class:
            # Reset for each attempt
            api._trello = None


            # First call
            instance1 = api._get_trello()
            # Second call
            instance2 = api._get_trello()

            # If we get here and the mock was called, we found the right path
            if mock_class.call_count > 0:
                # Verify the constructor was only called once
                mock_class.assert_called_once()
                # Verify both instances are the same
                assert instance1 is instance2
                # Verify it's our mock instance
                assert instance1 == mock_class.return_value
                return

    pytest.fail("Could not find correct patch path for TrelloManager")

def test_create_card(mock_trello_manager: MagicMock, sample_card: TrelloCard) -> None:
    """Test creating a new card."""
    mock_trello_manager.create_card.return_value = sample_card

    result = create_card(
        list_id="list123",
        name="Test Card",
        description="Test Description",
        due_date=datetime(2024, 12, 31, tzinfo=UTC)
    )

    assert isinstance(result, TrelloCard)
    assert result.name == "Test Card"
    assert result.desc == "Test Description"
    mock_trello_manager.create_card.assert_called_once()

def test_add_attachment(mock_trello_manager: MagicMock) -> None:
    """Test adding an attachment to a card."""
    mock_trello_manager.add_attachment.return_value = True

    result = add_attachment(
        card_id="card123",
        url="https://example.com",
        name="Test Attachment"
    )

    assert result is True
    mock_trello_manager.add_attachment.assert_called_once_with(
        "card123",
        "https://example.com",
        "Test Attachment"
    )

def test_create_checklist(mock_trello_manager: MagicMock) -> None:
    """Test creating a checklist."""
    expected = TrelloChecklist(
        id="checklist123",
        name="Test Checklist",
        items=[]
    )
    mock_trello_manager.create_checklist.return_value = expected

    result = create_checklist("card123", "Test Checklist")

    assert isinstance(result, TrelloChecklist)
    assert result.name == "Test Checklist"
    mock_trello_manager.create_checklist.assert_called_once()

def test_add_checklist_item(mock_trello_manager: MagicMock) -> None:
    """Test adding an item to a checklist."""
    expected: dict[str, Any] = {
        "id": "item123",
        "name": "Test Item",
        "checked": False
    }
    mock_trello_manager.add_checklist_item.return_value = expected

    result = add_checklist_item(
        checklist_id="checklist123",
        name="Test Item",
        checked=False
    )

    assert result == expected
    mock_trello_manager.add_checklist_item.assert_called_once_with(
        checklist_id="checklist123",
        name="Test Item",
        checked=False
    )

def test_update_card_due_date(mock_trello_manager: MagicMock) -> None:
    """Test updating a card's due date."""
    mock_trello_manager.update_card_due_date.return_value = True
    due_date = datetime(2024, 12, 31, tzinfo=UTC)

    result = update_card_due_date("card123", due_date)

    assert result is True
    mock_trello_manager.update_card_due_date.assert_called_once_with(
        "card123",
        due_date
    )

def test_search_cards(mock_trello_manager: MagicMock, sample_card: TrelloCard) -> None:
    """Test searching for cards."""
    mock_trello_manager.search_cards.return_value = [sample_card]

    results = search_cards("test", board_id="board123")

    assert len(results) == 1
    assert isinstance(results[0], TrelloCard)
    assert results[0].name == "Test Card"
    mock_trello_manager.search_cards.assert_called_once_with("test", "board123")

def test_get_board_lists(mock_trello_manager: MagicMock) -> None:
    """Test getting lists from a board."""
    expected = ["list1", "list2"]
    mock_trello_manager.get_lists.return_value = expected

    results = get_board_lists("board123")

    assert results == expected
    mock_trello_manager.get_lists.assert_called_once_with("board123")

def test_add_comment(mock_trello_manager: MagicMock) -> None:
    """Test adding a comment to a card."""
    mock_trello_manager.add_comment_to_card.return_value = True

    result = add_comment("card123", "Test comment")

    assert result is True
    mock_trello_manager.add_comment_to_card.assert_called_once_with(
        "card123",
        "Test comment"
    )

def test_add_label(mock_trello_manager: MagicMock) -> None:
    """Test adding a label to a card."""
    mock_trello_manager.add_label_to_card.return_value = True

    result = add_label("card123", "Priority", "red")

    assert result is True
    mock_trello_manager.add_label_to_card.assert_called_once_with(
        "card123",
        "Priority",
        "red"
    )

def test_move_card(mock_trello_manager: MagicMock) -> None:
    """Test moving a card to a different list."""
    mock_trello_manager.move_card.return_value = True

    result = move_card("card123", "list456")

    assert result is True
    mock_trello_manager.move_card.assert_called_once_with("card123", "list456")

def test_archive_card(mock_trello_manager: MagicMock) -> None:
    """Test archiving a card."""
    mock_trello_manager.archive_card.return_value = True

    result = archive_card("card123")

    assert result is True
    mock_trello_manager.archive_card.assert_called_once_with("card123")

def test_get_list_name(mock_trello_manager: MagicMock) -> None:
    """Test getting a list name."""
    mock_trello_manager.get_list_name.return_value = "Test List"

    result = get_list_name("list123")

    assert result == "Test List"
    mock_trello_manager.get_list_name.assert_called_once_with("list123")

def test_create_list(mock_trello_manager: MagicMock) -> None:
    """Test creating a new list."""
    mock_trello_manager.create_a_list.return_value = "list123"

    result = create_list("Test List", "board123")

    assert result == "list123"
    mock_trello_manager.create_a_list.assert_called_once_with(
        "Test List",
        "board123"
    )
