from flask import Flask, request, jsonify, redirect, url_for
import threading
import requests
from utils.slack_utils import process_event, send_message
from utils.trello_utils import create_trello_card
from utils.config import CLIENT_ID, CLIENT_SECRET

app = Flask(__name__)
processed_event_ids = set()

# Background thread to periodically clear processed IDs
def clear_processed_ids():
    import time
    while True:
        time.sleep(300)
        processed_event_ids.clear()

threading.Thread(target=clear_processed_ids, daemon=True).start()

# Slack Events Endpoint
@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    # Handle Slack challenge verification
    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    # Process Slack events
    if "event" in data:
        event = data["event"]
        event_id = data.get("event_id")

        if event_id in processed_event_ids:
            return "", 200

        processed_event_ids.add(event_id)
        threading.Thread(target=process_event, args=(event,)).start()

    return "", 200

@app.route("/create_card", methods=["POST"])
def create_card():
    data = request.form  # Parse form data sent by curl or Slack
    board_name = data.get("board_name")
    list_name = data.get("list_name")
    card_name = data.get("card_name")
    card_desc = data.get("card_desc", "")

    # Call the placeholder Trello function
    result = create_trello_card(board_name, list_name, card_name, card_desc)
    return jsonify({"message": result})


# Slack OAuth Callback Endpoint
@app.route('/oauth/callback', methods=['GET', 'POST'])
def oauth_callback():
    code = request.args.get("code")
    if not code:
        return "Error: Missing authorization code.", 400

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": code,
        "redirect_uri": "https://ripe-rooms-own.loca.lt",
    }

    try:
        response = requests.post("https://slack.com/api/oauth.v2.access", data=data)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"Failed to connect to Slack's OAuth API: {e}", 500

    response_json = response.json()
    if response_json.get("ok"):
        return redirect(url_for("success"))
    else:
        return f"Failed to retrieve access token: {response_json.get('error', 'Unknown error')}", 400
    
@app.route("/test", methods=["GET"])
def test():
    return {"message": "Server is running!"}, 200

# Success Endpoint
@app.route('/success', methods=['GET'])
def success():
    return "OAuth flow completed successfully!"

# Example Endpoint for Testing
@app.route('/slack/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Slackbot is running!"})

if __name__ == '__main__':
    app.run(port=3000, debug=True)
