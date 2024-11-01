# Trello Manager Module

A Python module for interacting with the Trello API, providing a simple interface for managing boards, lists, cards, and other Trello resources.

## Features

- Card Management (create, move, archive)
- List Management (create, get)
- Board Information Retrieval
- Attachment Handling
- Checklist Management
- Member Management
- Label Management
- Comment Management
- Rate Limit Handling
- Automatic Retries
- Error Handling

## Prerequisites

- Python 3.11+
- Trello API Key and OAuth Token
- Required Python packages (installed via pip):
  - requests
  - python-dotenv
  - pydantic 

## Installation

1. Ensure you have the required environment variables:
   - TRELLO_API_KEY
   - TRELLO_OAUTH_TOKEN

2. Create a `.env` file in your project root with these credentials.

## Getting Trello Credentials

1. Log in to Trello and visit: https://trello.com/app-key
2. Get your API Key
3. Generate a Token with appropriate permissions
4. Add both to your `.env` file

## Class Overview

### TrelloManager

Main class for interacting with the Trello API.

#### Key Methods:
```python
def create_card(list_id: str, name: str, desc: str = "", due_date: Optional[datetime] = None) -> TrelloCard
def add_attachment(card_id: str, url: str, name: Optional[str] = None) -> bool
def create_checklist(card_id: str, name: str) -> TrelloChecklist
def add_checklist_item(checklist_id: str, name: str, checked: bool = False) -> Dict[str, Any]
def update_card_due_date(card_id: str, due_date: Optional[datetime]) -> bool
def add_member_to_card(card_id: str, member_id: str) -> bool
def remove_member_from_card(card_id: str, member_id: str) -> bool
def get_board_members(board_id: str) -> List[Dict[str, Any]]
def search_cards(query: str, board_id: Optional[str] = None) -> List[TrelloCard]
def add_comment_to_card(card_id: str, comment: str) -> bool
def add_label_to_card(card_id: str, label_name: str, color: str = "blue") -> bool
def move_card(card_id: str, target_list_id: str) -> bool
def archive_card(card_id: str) -> bool
```

### Data Classes

#### TrelloCard
```python
@dataclass
class TrelloCard:
id: str
name: str
desc: str
url: str
board_id: str
list_id: str
due_date: Optional[datetime] = None
members: List[str] = None
labels: List[Dict[str, str]] = None
```

#### TrelloChecklist
```python
@dataclass
class TrelloChecklist:
id: str
name: str
items: List[Dict[str, Any]]
```

## Error Handling

The module includes custom exceptions for better error handling:

- `TrelloError`: Base exception for Trello-related errors
- `TrelloAPIError`: Raised for API request failures
- `TrelloRateLimitError`: Raised when hitting rate limits

## Testing

The module includes comprehensive tests. Run them using:

```bash
pytest --cov=src.trello --cov-report=term-missing
```

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
