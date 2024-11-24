"""Tests for the TrelloManager module.

This module contains tests for the internal TrelloManager class that handles direct
interactions with the Trello API. It verifies proper handling of API requests,
responses, and error conditions.
"""
import datetime
from unittest.mock import MagicMock, patch

import pytest
import requests

from src.maigic_nyu.trello._trello_manager import (
    TrelloCard,
    TrelloChecklist,
    TrelloManager,
    _TrelloAPIError,
    _TrelloError,
    _TrelloRateLimitError,
)


# Test fixtures
@pytest.fixture
def trello_manager():
    """Create a TrelloManager instance with test credentials."""
    with patch.dict("os.environ", {
        "TRELLO_API_KEY": "test_key",
        "TRELLO_OAUTH_TOKEN": "test_token"
    }, clear=True):
        with patch("src.maigic_nyu.trello._trello_manager.load_dotenv"):
            return TrelloManager()

@pytest.fixture
def mock_response():
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "id": "card123",
        "name": "Test Card",
        "desc": "Test Description",
        "shortUrl": "https://trello.com/c/abc123",
        "idBoard": "board123",
        "idList": "list123",
        "due": "2024-03-20T10:00:00Z",
        "idMembers": ["member123"],
        "labels": [{"id": "label123", "name": "Priority", "color": "red"}]
    }
    return response

# Test cases
def test_trello_manager_initialization() -> None:
    """Test TrelloManager initialization with missing credentials."""
    # Mock load_dotenv and clear environment variables
    with patch("src.maigic_nyu.trello._trello_manager.load_dotenv"), \
         patch.dict("os.environ", {}, clear=True):
        with pytest.raises(_TrelloError) as exc_info:
            TrelloManager()
        assert str(exc_info.value) == "Missing Trello API credentials"

def test_make_request_success(trello_manager, mock_response) -> None:
    """Test successful API request."""
    with patch("requests.request", return_value=mock_response):
        result = trello_manager._make_request("get", "/test")
        assert result == mock_response.json()

def test_make_request_rate_limit(trello_manager) -> None:
    """Test rate limit handling."""
    mock_rate_limit_response = MagicMock()
    mock_rate_limit_response.status_code = 429
    mock_rate_limit_response.headers = {"Retry-After": "1"}

    with patch("requests.request", return_value=mock_rate_limit_response):
        with pytest.raises(_TrelloRateLimitError):
            trello_manager._make_request("get", "/test")

def test_make_request_error(trello_manager) -> None:
    """Test API error handling."""
    with patch("requests.request", side_effect=requests.exceptions.RequestException):
        with pytest.raises(_TrelloAPIError):
            trello_manager._make_request("get", "/test")

def test_create_card_success(trello_manager, mock_response) -> None:
    """Test successful card creation."""
    with patch("requests.request", return_value=mock_response):
        card = trello_manager.create_card(
            list_id="list123",
            name="Test Card",
            desc="Test Description",
            due_date=datetime.datetime.fromisoformat("2024-03-20T10:00:00Z")
        )
        assert isinstance(card, TrelloCard)
        assert card.id == "card123"
        assert card.name == "Test Card"
        assert card.list_id == "list123"

def test_add_attachment(trello_manager, mock_response) -> None:
    """Test adding attachment to card."""
    with patch("requests.request", return_value=mock_response):
        result = trello_manager.add_attachment(
            card_id="card123",
            url="https://example.com",
            name="Test Attachment"
        )
        assert result is True

def test_create_checklist(trello_manager) -> None:
    """Test creating a checklist."""
    mock_checklist_response = MagicMock()
    mock_checklist_response.status_code = 200
    mock_checklist_response.json.return_value = {
        "id": "checklist123",
        "name": "Test Checklist",
        "checkItems": []
    }

    with patch("requests.request", return_value=mock_checklist_response):
        checklist = trello_manager.create_checklist(
            card_id="card123",
            name="Test Checklist"
        )
        assert isinstance(checklist, TrelloChecklist)
        assert checklist.id == "checklist123"
        assert checklist.name == "Test Checklist"

def test_add_checklist_item(trello_manager, mock_response) -> None:
    """Test adding item to checklist."""
    with patch("requests.request", return_value=mock_response):
        result = trello_manager.add_checklist_item(
            checklist_id="checklist123",
            name="Test Item",
            checked=False
        )
        assert result == mock_response.json()

def test_update_card_due_date(trello_manager, mock_response) -> None:
    """Test updating card due date."""
    with patch("requests.request", return_value=mock_response):
        result = trello_manager.update_card_due_date(
            card_id="card123",
            due_date=datetime.datetime.now()
        )
        assert result is True
def test_search_cards(trello_manager, mock_response) -> None:
    """Test searching cards."""
    mock_search_response = MagicMock()
    mock_search_response.status_code = 200
    mock_search_response.json.return_value = {
        "cards": [mock_response.json()]
    }

    with patch("requests.request", return_value=mock_search_response):
        cards = trello_manager.search_cards("test query", "board123")
        assert len(cards) == 1
        assert isinstance(cards[0], TrelloCard)
        assert cards[0].id == "card123"

def test_validate_board_access(trello_manager, mock_response) -> None:
    """Test board access validation."""
    with patch("requests.request", return_value=mock_response):
        assert trello_manager.validate_board_access("board123") is True

    with patch("requests.request", side_effect=_TrelloAPIError):
        assert trello_manager.validate_board_access("invalid_board") is False

# Integration test example (disabled by default)
@pytest.mark.skip(reason="Integration test requiring real credentials")
def test_integration_create_card() -> None:
    """Integration test for card creation (requires real credentials)."""
    manager = TrelloManager()
    card = manager.create_card(
        list_id="your_test_list_id",
        name="Integration Test Card",
        desc="This is a test card created by pytest"
    )
    assert isinstance(card, TrelloCard)
    assert card.name == "Integration Test Card"

def test_get_full_board_info_success(trello_manager) -> None:
    """Test successful board info retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "full_board_id_123"}

    with patch("requests.get", return_value=mock_response):
        board_id = trello_manager.get_full_board_info("short_board_id")
        assert board_id == "full_board_id_123"

def test_get_full_board_info_failure(trello_manager) -> None:
    """Test failed board info retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        board_id = trello_manager.get_full_board_info("invalid_board_id")
        assert board_id == ""

def test_get_lists_success(trello_manager) -> None:
    """Test successful lists retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [
        {"id": "list1", "name": "To Do"},
        {"id": "list2", "name": "Done"}
    ]

    with patch("requests.get", return_value=mock_response):
        lists = trello_manager.get_lists("board_id")
        assert len(lists) == 2
        assert "list1" in lists
        assert "list2" in lists

def test_get_lists_failure(trello_manager) -> None:
    """Test failed lists retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        lists = trello_manager.get_lists("invalid_board_id")
        assert lists == []

def test_get_list_name_success(trello_manager) -> None:
    """Test successful list name retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "Test List"}

    with patch("requests.get", return_value=mock_response):
        name = trello_manager.get_list_name("list_id")
        assert name == "Test List"

def test_get_list_name_failure(trello_manager) -> None:
    """Test failed list name retrieval."""
    mock_response = MagicMock()
    mock_response.status_code = 404

    with patch("requests.get", return_value=mock_response):
        name = trello_manager.get_list_name("invalid_list_id")
        assert name == ""

def test_create_a_list_success(trello_manager) -> None:
    """Test successful list creation."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "new_list_id"}

    with patch("requests.post", return_value=mock_response):
        list_id = trello_manager.create_a_list("New List", "board_id")
        assert list_id == "new_list_id"

def test_create_a_list_failure(trello_manager) -> None:
    """Test failed list creation."""
    mock_response = MagicMock()
    mock_response.status_code = 400

    with patch("requests.post", return_value=mock_response):
        list_id = trello_manager.create_a_list("New List", "invalid_board_id")
        assert list_id == ""

def test_add_comment_to_card_success(trello_manager) -> None:
    """Test successful comment addition."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("requests.post", return_value=mock_response):
        result = trello_manager.add_comment_to_card("card_id", "Test comment")
        assert result is True

def test_add_comment_to_card_failure(trello_manager) -> None:
    """Test failed comment addition."""
    mock_response = MagicMock()
    mock_response.status_code = 400

    with patch("requests.post", return_value=mock_response):
        result = trello_manager.add_comment_to_card("invalid_card_id", "Test comment")
        assert result is False

def test_add_label_to_card_success(trello_manager) -> None:
    """Test successful label addition."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("requests.post", return_value=mock_response):
        result = trello_manager.add_label_to_card("card_id", "Test Label", "green")
        assert result is True

def test_add_label_to_card_failure(trello_manager) -> None:
    """Test failed label addition."""
    mock_response = MagicMock()
    mock_response.status_code = 400

    with patch("requests.post", return_value=mock_response):
        result = trello_manager.add_label_to_card("invalid_card_id", "Test Label")
        assert result is False

def test_move_card_success(trello_manager) -> None:
    """Test successful card move."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("requests.put", return_value=mock_response):
        result = trello_manager.move_card("card_id", "new_list_id")
        assert result is True

def test_move_card_failure(trello_manager) -> None:
    """Test failed card move."""
    mock_response = MagicMock()
    mock_response.status_code = 400

    with patch("requests.put", return_value=mock_response):
        result = trello_manager.move_card("invalid_card_id", "new_list_id")
        assert result is False

def test_archive_card_success(trello_manager) -> None:
    """Test successful card archival."""
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("requests.put", return_value=mock_response):
        result = trello_manager.archive_card("card_id")
        assert result is True

def test_archive_card_failure(trello_manager) -> None:
    """Test failed card archival."""
    mock_response = MagicMock()
    mock_response.status_code = 400

    with patch("requests.put", return_value=mock_response):
        result = trello_manager.archive_card("invalid_card_id")
        assert result is False

def test_make_request_network_error(trello_manager) -> None:
    """Test network error handling in make_request."""
    with patch("requests.request", side_effect=requests.exceptions.ConnectionError):
        with pytest.raises(_TrelloAPIError) as exc_info:
            trello_manager._make_request("get", "/test")
        assert "API request failed" in str(exc_info.value)

def test_make_request_timeout(trello_manager) -> None:
    """Test timeout handling in make_request."""
    with patch("requests.request", side_effect=requests.exceptions.Timeout):
        with pytest.raises(_TrelloAPIError) as exc_info:
            trello_manager._make_request("get", "/test")
        assert "API request failed" in str(exc_info.value)

def test_make_request_retry_success(trello_manager, mock_response) -> None:
    """Test successful retry after initial failure."""
    mock_fail = MagicMock()
    mock_fail.status_code = 429
    mock_fail.headers = {"Retry-After": "1"}

    with patch("requests.request", side_effect=[mock_fail, mock_response]):
        result = trello_manager._make_request("get", "/test")
        assert result == mock_response.json()
