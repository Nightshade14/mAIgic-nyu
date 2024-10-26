import os.path
from typing import ClassVar
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os


class Gmail:
    SCOPES: ClassVar[list[str]] = ["https://www.googleapis.com/auth/gmail.readonly"]

    def __init__(self) -> None:
        self._client = self.authenticate()

    def authenticate(self):
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", self.SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.getenv("CREDENTIALS_FILE_NAME"), self.SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open("token.json", "w") as token:
                token.write(creds.to_json())
        return build("gmail", "v1", credentials=creds, cache_discovery=False)

    def query(self):
        results = (
            self._client.users()
            .messages()
            .list(userId="me", labelIds=["INBOX"], maxResults=10000)
            .execute()
        )
        messages = results.get("messages", [])

        for message in messages:
            yield message

    def get_message(self, message_id: str):
        return self._client.users().messages().get(userId="me", id=message_id).execute()
    