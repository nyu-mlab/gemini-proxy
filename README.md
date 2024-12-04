
# Gemini Proxy API Documentation

This document explains how to use the **Gemini Proxy API**, hosted at [https://gemini-proxy.hdanny.org](https://gemini-proxy.hdanny.org). The API provides an interface for interacting with the Gemini generative model, allowing users to start a chat session, send messages, and end a chat session. Example Python code demonstrates usage.

---

## Base URL

```
https://gemini-proxy.hdanny.org
```

---

## Endpoints

### 1. **Start a Chat**
**Endpoint**: `/start_chat`
**Method**: `POST`

This endpoint initializes a chat session using the specified model and configuration.

#### Request Parameters
- **user_id** (string, required): The ID of the user starting the chat. Must be a valid user as defined in `valid_users.txt`. If you don't know the user ID, please contact the administrator (Danny Y. Huang).
- **model_name** (string, optional): The name of the generative model to use (default: `"gemini-1.5-flash-002"`).
- **generation_config** (object, optional): Configuration for the model's behavior. Example:
  ```json
  {
      "max_output_tokens": 1000,
      "temperature": 0.7,
      "top_p": 0.9
  }
  ```

#### Response
- **200 OK**: Returns the unique `chat_id` for the session.
- **403 Forbidden**: Invalid or missing `user_id`.
- **500 Internal Server Error**: Error in processing the request.

#### Example Request
```python
url = "https://gemini-proxy.hdanny.org/start_chat"
payload = {
    "user_id": "user1",
    "model_name": "gemini-1.5-flash-002",
    "generation_config": {
        "max_output_tokens": 1000,
        "temperature": 0.7,
        "top_p": 0.9
    }
}
response = requests.post(url, json=payload)
chat_id = response.json()["chat_id"]
print(chat_id)
```

---

### 2. **Send a Message**
**Endpoint**: `/send_message`
**Method**: `POST`

This endpoint sends a message to the active chat session.

#### Request Parameters
- **chat_id** (string, required): The unique ID of the chat session, returned from `/start_chat`.
- **message** (string, required): The message to send to the model.

#### Response
- **200 OK**: Returns the model's response to the message.
- **404 Not Found**: Invalid or missing `chat_id`.
- **429 Too Many Requests**: Rate limit exceeded (at most 2 requests per second per user).
- **500 Internal Server Error**: Error in processing the request.

#### Example Request
```python
url = "https://gemini-proxy.hdanny.org/send_message"
payload = {
    "chat_id": "chat_id_from_start_chat",
    "message": "What is the capital of California?"
}
response = requests.post(url, json=payload)
model_response = response.json()["response"]
print(model_response)
```

---

### 3. **End a Chat**
**Endpoint**: `/end_chat`
**Method**: `POST`

This endpoint terminates an active chat session.

#### Request Parameters
- **chat_id** (string, required): The unique ID of the chat session.

#### Response
- **200 OK**: Confirms the chat session has ended.
- **404 Not Found**: Invalid or missing `chat_id`.
- **500 Internal Server Error**: Error in processing the request.

#### Example Request
```python
url = "https://gemini-proxy.hdanny.org/end_chat"
payload = {"chat_id": "chat_id_from_start_chat"}
response = requests.post(url, json=payload)
end_message = response.json()["message"]
print(end_message)
```

---

## Rate Limits

- Each user is limited to **2 `send_message` calls per second**.
- Exceeding the rate limit returns a **429 Too Many Requests** error.

---

## Logging

All interactions with the API are logged in JSON format. Each log entry includes:
- **timestamp**: ISO 8601 timestamp of the interaction.
- **user_id**: The ID of the user making the request.
- **message**: The message sent by the user.
- **output_length**: The length of the model's response.

Example log entry:
```json
{
    "timestamp": "2024-12-04T10:15:30.123Z",
    "user_id": "user1",
    "message": "What is the capital of California?",
    "output_length": 42
}
```

---

## Example Usage in Python

The following Python script demonstrates a complete workflow: starting a chat, sending messages, and ending the chat. Note that the code below should work out-of-the-box, provided that you have the valid `user_id`. If you don't have a `user_id`, please contact the administrator (Danny Y. Huang).

```python
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
    USER_ID = "user1"
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
```

---

## Notes
- Ensure the `valid_users.txt` file contains your user ID before making requests.
- For secure interactions, ensure HTTPS is properly configured and certificates are valid.
- If rate limits are exceeded, consider introducing a delay between consecutive `send_message` calls.

---

This documentation should help you effectively interact with the Gemini Proxy API.
