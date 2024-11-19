"""
trello_service.py

This module provides higher-level business logic for Trello operations, such as
finding or creating lists, and creating cards based on email content.
"""
import os
from dotenv import load_dotenv
from datetime import datetime
from maigic_nyu.trello._trello import TrelloAPI

class TrelloService:
    def __init__(self):
        self.trello_api = TrelloAPI()
        load_dotenv()
        self.board_id = os.getenv("TRELLO_BOARD_ID")
        if not self.board_id:
            raise ValueError("Missing Trello board ID in environment variables")

    def create_card(
            self,
            card_type: str,
            card_name: str,
            card_desc: str,
            due_date: datetime = None
    ):
        if card_type.lower() == "meeting":
            list_name = "Meeting"
        elif card_type.lower() == "event":
            list_name = "Events"
        else:
            list_name = "General"

        list_id = self.find_or_create_list(list_name)

        card = self.trello_api.create_card(
            list_id=list_id,
            name=card_name,
            desc=card_desc,
            due_date=due_date,
        )

        result = {
            "id": card["id"],
            "name": card["name"],
            "url": card["shortUrl"],
        }

        return result

    def find_or_create_list(self, list_name: str) -> str:
        """Find or create a list by name."""
        lists = self.trello_api.get_lists(self.board_id)
        for lst_id in lists:
            if self.trello_api.get_list_name(lst_id) == list_name:
                return lst_id
        return self.trello_api.create_a_list(list_name, self.board_id)
