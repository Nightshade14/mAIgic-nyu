"""Test file for Gmail class."""  # noqa: INP001

# pytest test/test_gmail.py -v

from datetime import datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest
import pytz

from maigic_nyu.gmail._client import Gmail


@pytest.fixture
def mock_gmail_service() -> Any:
    """Fixture to mock the Gmail API service."""
    with patch("maigic_nyu.gmail._client.build") as mock_build:
        mock_service = Mock()
        mock_build.return_value = mock_service
        yield mock_service


MESSAGE_LEN = 2


@pytest.fixture
def gmail_client() -> Any:
    """Fixture to create a Gmail client with mocked authentication."""
    with patch("maigic_nyu.gmail._client.Credentials") as mock_creds:
        mock_creds.from_authorized_user_file.return_value = Mock(valid=True)
        return Gmail()


def test_query_method(gmail_client: Any, mock_gmail_service: Any) -> Any:
    """Test the query method of the Gmail client.

    Args:
        gmail_client: The Gmail client fixture
        mock_gmail_service: The mocked Gmail service fixture

    """
    # Mock response data
    mock_messages = {
        "messages": [
            {"id": "123", "threadId": "thread123"},
            {"id": "456", "threadId": "thread456"},
        ]
    }

    # Setup the mock chain
    mock_service = mock_gmail_service
    (
        mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value
    ) = mock_messages

    # Test the query method
    start_date = datetime(2024, 10, 30, tzinfo=pytz.UTC)
    end_date = datetime(2024, 10, 31, tzinfo=pytz.UTC)
    messages = list(
        gmail_client.query(start_date=start_date, end_date=end_date, max_results=5)
    )

    # Assertions
    assert len(messages) == MESSAGE_LEN
    assert messages[0]["id"] == "123"
    assert messages[1]["id"] == "456"

    # Verify the correct query parameters were used
    mock_service.users.return_value.messages.return_value.list.assert_called_with(
        userId="me", maxResults=5, q="after:2024/10/30 AND before:2024/10/31"
    )


def test_get_message(gmail_client: Any, mock_gmail_service: Any) -> Any:
    """Test the get_message method of the Gmail client.

    Args:
        gmail_client: The Gmail client fixture
        mock_gmail_service: The mocked Gmail service fixture

    """
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
    (
        mock_service.users.return_value.messages.return_value.get.return_value.execute.return_value
    ) = mock_message

    # Test get_message
    result = gmail_client.get_message("123")

    # Assertions
    assert result == mock_message
    assert result["payload"]["headers"][0]["value"] == "Test Subject"

    # Verify the correct parameters were used
    mock_service.users.return_value.messages.return_value.get.assert_called_with(
        userId="me", id="123"
    )
