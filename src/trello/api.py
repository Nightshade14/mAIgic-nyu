# A data class representing a Trello card, encapsulating its attributes and initializing default values for members and labels.
from src.trello.trello_manager import TrelloCard

# A data class representing a Trello checklist, containing its ID, name, and items.
from src.trello.trello_manager import TrelloChecklist

# A class that interacts with the Trello API, providing methods to manage cards, lists, and other Trello resources while handling API requests and responses.
from src.trello.trello_manager import TrelloManager

# TrelloManager comes with the following methods:
# 1. create_card: Creates a new Trello card in a specified list with optional description and due date.
# 2. add_attachment: Adds an attachment to a specified Trello card.
# 3. create_checklist: Creates a new checklist on a specified Trello card.
# 4. add_checklist_item: Adds an item to a specified checklist.
# 5. update_card_due_date: Updates or removes the due date of a specified Trello card.
# 6. search_cards: Searches for cards based on a query, with an optional filter for a specific board.
# 7. get_full_board_info: Retrieves the full ID of a Trello board using its short ID.
# 8. get_lists: Retrieves all lists in a specified Trello board.
# 9. add_comment_to_card: Adds a comment to a specified Trello card.
# 10. add_label_to_card: Adds a label to a specified Trello card with a given name and color.
# 11. move_card: Moves a specified Trello card to a different list.
# 12. archive_card: Archives (closes) a specified Trello card.
# 13. get_list_name: Retrieves the name of a specified list using its ID.
# 14. create_a_list: Creates a new list on a specified Trello board and returns its ID.
# 15. validate_board_access: Validates whether the current API credentials have access to a specified Trello board.
