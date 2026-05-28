import requests
import os

# Example API call with streaming support
invoke_url = "https://api.example.com/invoke"  # Replace with your actual API URL

# Get API key from environment variable
api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY environment variable is not set")

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Define the payload with chat_template_kwargs
payload = {
    "model": "your-model-name",
    "messages": [
        {"role": "user", "content": "Hello, how are you?"}
    ],
    "stream": True,
    "chat_template_kwargs": {"thinking": True}
}

# Make the request with streaming
stream = True
try:
    response = requests.post(invoke_url, headers=headers, json=payload, stream=stream)
    response.raise_for_status()
    
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
