# In order to test Google Auth, actual message in your Gmail and API. You can 
# replace specific info (like start/end date or message_id) in this file.
# Then compare the output with the actual output in your Gmail.

from datetime import datetime
from src.gmail.API import query, get_message, get_labels, search

## Query Messages Example
# Get messages from a specific date range
start_date = datetime(2024, 10, 31)
end_date = datetime(2024, 11, 1)
messages = query(start_date=start_date, end_date=end_date, max_results=5)
for msg in messages:
    print(f"Message ID: {msg['id']}, Thread ID: {msg['threadId']}")

## Get Single Message Example
# Fetch details of a specific message
message_id = "192e80bb14e565c5" 
message = get_message(message_id)
print(f"Subject: {message.get('subject')}")
print(f"Snippet: {message.get('snippet')}")

## Get Labels Example
# Fetch all Gmail labels
labels = get_labels()
for label in labels:
    print(f"Label Name: {label['name']}, Label ID: {label['id']}")

## Search Example
# Search for specific emails
search_query = "aaa"
search_results = search(query=search_query, max_results=5)
for result in search_results:
    message_details = get_message(result["id"])
    print(f"Found message: {message_details.get('snippet')}")
