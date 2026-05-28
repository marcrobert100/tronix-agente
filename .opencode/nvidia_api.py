import os
import base64
import requests

def read_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# Configuration
stream = True
invoke_url = "https://api.nvidia.com/v1/chat/completions"

# Get API key from environment variable (recommended for security)
api_key = os.getenv("NVIDIA_API_KEY")
if not api_key:
    raise ValueError("NVIDIA_API_KEY environment variable is not set")

# Headers
headers = {
    "Authorization": f"Bearer {api_key}",
    "Accept": "text/event-stream" if stream else "application/json"
}

# Payload
payload = {
    "model": "nvidia/llama-3.1-nemotron-70b-instruct",  # Valid NVIDIA model
    "messages": [{"role":"user","content":"Hello, how are you?"}],
    "max_tokens": 16384,
    "temperature": 1.00,
    "top_p": 1.00,
    "stream": stream,
    # "chat_template_kwargs": {"thinking":True},  # Remove if not supported by the model
}

# Request
response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)

# Response handling
if stream:
    for line in response.iter_lines():
        if line:
            print(line.decode("utf-8"))
else:
    print(response.json())
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
    if 'response' in locals():
        print(f"Response status: {response.status_code}")
        print(f"Response text: {response.text}")
