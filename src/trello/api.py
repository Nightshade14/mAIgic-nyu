"""
api.py

This module provides a simplified interface for interacting with Trello.
It hides the implementation details of TrelloService and TrelloAPI.
"""
from trello_service import TrelloService


class TrelloAPI:
    def __init__(self):
        self.service = TrelloService()

    def create_card(self, card_type: str, card_name: str, card_desc: str, due_date=None):
        return self.service.create_card(card_type, card_name, card_desc, due_date)