import requests
import json

# Test the backend API
BASE_URL = "http://localhost:8000"

# Test 1: Check if backend is running
try:
    response = requests.get(BASE_URL + "/")
    print("Backend status:", response.status_code)
    print("Backend response:", response.json())
except Exception as e:
    print("Backend not accessible:", e)

# Test 2: Check health endpoint
try:
    response = requests.get(BASE_URL + "/health")
    print("Health check:", response.status_code, response.json())
except Exception as e:
    print("Health check failed:", e)