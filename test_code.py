import requests

BASE_URL = "https://gemini-proxy.hdanny.org"

# Step 1: Start a Chat
def start_chat(user_id, model_name, generation_config):
    url = f"{BASE_URL}/start_chat"
    payload = {
        "user_id": user_id,
        "model_name": model_name,
        "generation_config": generation_config,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["chat_id"]

# Step 2: Send a Message
def send_message(chat_id, message):
    url = f"{BASE_URL}/send_message"
    payload = {
        "chat_id": chat_id,
        "message": message,
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["response"]

# Step 3: End the Chat
def end_chat(chat_id):
    url = f"{BASE_URL}/end_chat"
    payload = {"chat_id": chat_id}
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()["message"]

# Example Usage
if __name__ == "__main__":
    USER_ID = "[ENTER_YOUR_USER_ID]"
    MODEL_NAME = "gemini-1.5-flash-002"
    GENERATION_CONFIG = {
        "max_output_tokens": 1000,
        "temperature": 0.7,
        "top_p": 0.9,
    }

    try:
        # Start a chat
        chat_id = start_chat(USER_ID, MODEL_NAME, GENERATION_CONFIG)
        print(f"Chat started with ID: {chat_id}")

        # Send messages
        response1 = send_message(chat_id, "What is the capital of California?")
        print(f"Response 1: {response1}")

        response2 = send_message(chat_id, "What about New Jersey?")
        print(f"Response 2: {response2}")

        # End the chat
        end_message = end_chat(chat_id)
        print(f"Chat ended: {end_message}")
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")