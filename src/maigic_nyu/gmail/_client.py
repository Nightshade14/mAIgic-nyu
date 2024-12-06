"""TODO: Add docstring."""

import os
import os.path
from collections.abc import Generator
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


class Gmail:
    """A class to interact with Gmail using the Gmail API.

    This class provides methods to authenticate with Gmail and perform
    various operations like fetching and filtering emails.

    """

    SCOPES: ClassVar[list[str]] = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self) -> None:
        """Initialize Gmail client with authenticated credentials."""
        self._client = self.authenticate()

    def authenticate(self) -> Any:
        """Authenticate with Gmail API using OAuth 2.0.

        Returns:
            An authenticated Gmail API service object.

        Raises:
            FileNotFoundError: If credentials file is not found.
            ValueError: If authentication fails.

        """
        creds = None
        if Path("token.json").exists():
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.getenv("CREDENTIALS_FILE_NAME"), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with Path("token.json").open("w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def query(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        max_results: int = 10000,
    ) -> Generator[dict, None, None]:
        """Query Gmail messages with filters.

        Args:
            start_date: Only return messages after this date
            end_date: Only return messages before this date
            max_results: Maximum number of messages to return

        Yields:
            Dict containing message metadata

        Search operators used:
            after:YYYY/MM/DD - Messages after date
            before:YYYY/MM/DD - Messages before date

        """
        query_parts = []

        if start_date:
            query_parts.append(f"after:{start_date.strftime('%Y/%m/%d')}")

        if end_date:
            query_parts.append(f"before:{end_date.strftime('%Y/%m/%d')}")

        query_string = " AND ".join(query_parts) if query_parts else ""

        results = (
            self._client.users()
            .messages()
            .list(userId="me", maxResults=max_results, q=query_string)
            .execute()
        )

        messages = results.get("messages", [])
        yield from messages

    def get_message(self, message_id: str) -> dict:
        """Fetch a specific email message by ID.

        Args:
            message_id: The ID of the message to fetch.

        Returns:
            Dict containing the message details.

        """
        return self._client.users().messages().get(userId="me", id=message_id).execute()
