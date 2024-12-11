from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from utils.config import SLACK_TOKEN

client = WebClient(token=SLACK_TOKEN)

def send_message(channel, message):
    try:
        client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print("Error sending message:", e.response["error"])

def process_event(event):
    if "bot_id" in event:
        return

    user_message = event["text"].lower()
    channel = event["channel"]

    if "hello" in user_message:
        send_message(channel, "Hello! How can I assist you?")
    elif "help" in user_message:
        send_message(channel, "Here are some commands you can use...")
    elif "add" in user_message:
        send_message(channel, "You can add tasks to Trello with the command: `add \"<task name>\" to trello`.")
    else:
        send_message(channel, "I didn't understand that.")
