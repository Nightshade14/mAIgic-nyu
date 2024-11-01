# pytest test/test_gmail.py -v
import pytest
from datetime import datetime
from unittest.mock import Mock, patch
from src.gmail.client import Gmail


@pytest.fixture
def mock_gmail_service():
    """Fixture to mock the Gmail API service"""
    with patch("src.gmail.client.build") as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        yield mock_service


@pytest.fixture
def gmail_client(mock_gmail_service):
    """Fixture to create a Gmail client with mocked authentication"""
    with patch("src.gmail.client.Credentials") as mock_creds:
        mock_creds.from_authorized_user_file.return_value = Mock(valid=True)
        return Gmail()


def test_query_method(gmail_client, mock_gmail_service):
    # Mock response data
    mock_messages = {
        "messages": [
            {"id": "123", "threadId": "thread123"},
            {"id": "456", "threadId": "thread456"},
        ]
    }

    # Setup the mock chain
    mock_service = mock_gmail_service
    mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = mock_messages

    # Test the query method
    start_date = datetime(2024, 10, 30)
    end_date = datetime(2024, 10, 31)
    messages = list(
        gmail_client.query(start_date=start_date, end_date=end_date, max_results=5)
    )

    # Assertions
    assert len(messages) == 2
    assert messages[0]["id"] == "123"
    assert messages[1]["id"] == "456"

    # Verify the correct query parameters were used
    mock_service.users.return_value.messages.return_value.list.assert_called_with(
        userId="me", maxResults=5, q="after:2024/10/30 AND before:2024/10/31"
    )


def test_get_message(gmail_client, mock_gmail_service):
    # Mock response data
    mock_message = {
        "id": "123",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "sender@example.com"},
            ]
        },
    }

    # Setup the mock
    mock_service = mock_gmail_service
    mock_service.users.return_value.messages.return_value.get.return_value.execute.return_value = mock_message

    # Test get_message
    result = gmail_client.get_message("123")

    # Assertions
    assert result == mock_message
    assert result["payload"]["headers"][0]["value"] == "Test Subject"

    # Verify the correct parameters were used
    mock_service.users.return_value.messages.return_value.get.assert_called_with(
        userId="me", id="123"
    )


def test_search_method(gmail_client, mock_gmail_service):
    # Mock response data
    mock_search_results = {
        "messages": [
            {"id": "789", "threadId": "thread789"},
            {"id": "012", "threadId": "thread012"},
        ]
    }

    # Setup the mock
    mock_service = mock_gmail_service
    mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = mock_search_results

    # Test search method
    search_query = "test query"
    results = list(gmail_client.search(search_query, max_results=2))

    # Assertions
    assert len(results) == 2
    assert results[0]["id"] == "789"
    assert results[1]["id"] == "012"

    # Verify the correct parameters were used
    mock_service.users.return_value.messages.return_value.list.assert_called_with(
        userId="me", maxResults=2, q=search_query
    )


def test_get_labels(gmail_client, mock_gmail_service):
    # Mock response data
    mock_labels = {
        "labels": [{"id": "INBOX", "name": "INBOX"}, {"id": "SENT", "name": "SENT"}]
    }

    # Setup the mock
    mock_service = mock_gmail_service
    mock_service.users.return_value.labels.return_value.list.return_value.execute.return_value = mock_labels

    # Test get_labels
    results = gmail_client.get_labels()

    # Assertions
    assert len(results) == 2
    assert results[0]["name"] == "INBOX"
    assert results[1]["name"] == "SENT"

    # Verify the correct parameters were used
    mock_service.users.return_value.labels.return_value.list.assert_called_with(
        userId="me"
    )
