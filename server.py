from flask import Flask, request, jsonify
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting
from uuid import uuid4
from time import time
import json
import threading
from datetime import datetime

app = Flask(__name__)

# Initialize Vertex AI
vertexai.init(project="rameen-network-ml", location="us-central1")

# Store active chats and user rate limits
active_chats = {}
rate_limits = {}
rate_lock = threading.Lock()

# Log file for messages
LOG_FILE = "chat_log.jsonl"

def is_valid_user(user_id):
    """Check if the user_id is in the valid_users.txt file."""
    user_id = user_id.strip()
    if not user_id:
        return False
    try:
        with open("valid_users.txt", "r") as f:
            valid_users = set(line.strip() for line in f)
        return user_id in valid_users
    except FileNotFoundError:
        return False


@app.route('/start_chat', methods=['POST'])
def start_chat():
    """Start a new chat session with a specified model and config."""
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        model_name = data.get("model_name", "gemini-1.5-flash-002")
        generation_config = data.get("generation_config", {
            "max_output_tokens": 8192,
            "temperature": 1,
            "top_p": 0.95,
        })

        if not user_id or not is_valid_user(user_id):
            return jsonify({"error": "Invalid or missing user_id"}), 403

        # Create the generative model
        model = GenerativeModel(model_name)
        chat_id = str(uuid4())  # Generate a unique chat ID
        chat = model.start_chat()
        active_chats[chat_id] = {
            "chat": chat,
            "user_id": user_id,
            "generation_config": generation_config,
        }
        return jsonify({"chat_id": chat_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/send_message', methods=['POST'])
def send_message():
    """Send a message to an existing chat session."""
    try:
        data = request.get_json()
        chat_id = data.get("chat_id")
        message = data.get("message")
        if not chat_id or not message:
            return jsonify({"error": "chat_id and message are required"}), 400

        chat_data = active_chats.get(chat_id)
        if not chat_data:
            return jsonify({"error": "Chat session not found"}), 404

        user_id = chat_data["user_id"]

        # Rate limiting
        with rate_lock:
            now = time()
            if user_id not in rate_limits:
                rate_limits[user_id] = []
            recent_calls = rate_limits[user_id]
            recent_calls = [t for t in recent_calls if now - t < 1]  # Keep only calls within the last second
            if len(recent_calls) >= 2:
                return jsonify({"error": "At most 2 send_message calls may be invoked every second"}), 429
            recent_calls.append(now)
            rate_limits[user_id] = recent_calls

        chat = chat_data["chat"]
        generation_config = chat_data["generation_config"]
        response = chat.send_message(
            [message],
            generation_config=generation_config,
        )
        output_length = len(response.text)

        # Log the message, user_id, output length, and timestamp in JSON format
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "message": message,
            "output_length": output_length,
        }
        with open(LOG_FILE, "a") as log_file:
            log_file.write(json.dumps(log_entry) + "\n")

        return jsonify({"response": response.text}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/end_chat', methods=['POST'])
def end_chat():
    """End a chat session."""
    try:
        data = request.get_json()
        chat_id = data.get("chat_id")
        if not chat_id:
            return jsonify({"error": "chat_id is required"}), 400

        if chat_id in active_chats:
            del active_chats[chat_id]
            return jsonify({"message": "Chat ended successfully"}), 200
        else:
            return jsonify({"error": "Chat session not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)