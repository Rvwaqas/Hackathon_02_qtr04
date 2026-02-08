import requests
import json

# Test the backend API directly
BASE_URL = "http://localhost:8000"

print("Testing TaskFlow Backend...")

# Test 1: Check backend
try:
    response = requests.get(BASE_URL + "/health")
    print("[OK] Backend is running:", response.json())
except Exception as e:
    print("[ERROR] Backend error:", e)

# Test 2: Try to get a list of users or check if there's a default admin
print("\nTrying to access tasks without authentication (should fail)...")
try:
    response = requests.get(BASE_URL + "/api/tasks")
    print("Unexpected success:", response.status_code, response.json())
except Exception as e:
    print("Expected failure (no auth):", type(e).__name__)

# Test 3: Try common default credentials
common_users = [
    {"email": "admin@example.com", "password": "password"},
    {"email": "admin@example.com", "password": "admin"},
    {"email": "admin@example.com", "password": "password123"},
    {"email": "user@example.com", "password": "password"},
    {"email": "test@example.com", "password": "password"},
]

print("\nTrying common default credentials...")
headers = {}

for user in common_users:
    try:
        response = requests.post(BASE_URL + "/api/auth/signin", json=user)
        if response.status_code == 200:
            result = response.json()
            print(f"[OK] Successfully signed in as {user['email']}")
            token = result.get('access_token')
            user_id = result.get('user', {}).get('id')
            print(f"  - User ID: {user_id}")
            print(f"  - Token: {token[:20]}...")
            
            # Test getting tasks with this token
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(BASE_URL + "/api/tasks", headers=headers)
            if response.status_code == 200:
                tasks = response.json()
                print(f"  - Found {len(tasks)} tasks")
                for task in tasks[-2:]:  # Show last 2 tasks
                    print(f"    - Task {task.get('id')}: {task.get('title')}")
            else:
                print(f"  - Could not get tasks: {response.status_code}")
            
            # Test chat functionality
            chat_data = {
                "message": "Add a test task",
                "conversation_id": None
            }
            response = requests.post(f"{BASE_URL}/api/{user_id}/chat", json=chat_data, headers=headers)
            if response.status_code == 200:
                chat_result = response.json()
                print(f"  - Chat response: {chat_result.get('message', '')[:50]}...")
            else:
                print(f"  - Chat failed: {response.status_code}")
            
            break
        else:
            print(f"  - Failed for {user['email']}: {response.status_code}")
    except Exception as e:
        print(f"  - Error for {user['email']}: {e}")
else:
    print("[INFO] No common credentials worked, need to create a new user.")

print("\nTest completed!")