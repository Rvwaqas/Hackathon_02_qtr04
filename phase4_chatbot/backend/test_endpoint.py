import requests
import time
import json

# Wait a bit for the server to start
time.sleep(5)

# Test the chat endpoint
try:
    # First test the health endpoint to see if the server is running
    health_response = requests.get("http://127.0.0.1:8003/health")
    print(f"Health check: {health_response.status_code}, {health_response.json()}")
    
    # Then test the chat endpoint (this will fail due to auth but will show if the route exists)
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer fake-token"
    }
    data = {
        "message": "Hello, test message"
    }
    
    response = requests.post("http://127.0.0.1:8003/api/1/chat", headers=headers, json=data)
    print(f"Chat endpoint test: {response.status_code}")
    print(f"Response: {response.text}")
    
except Exception as e:
    print(f"Error testing endpoints: {e}")