import requests
import json

# Test the full application flow
BASE_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

print("Testing TaskFlow Application...")

# Test 1: Check backend
try:
    response = requests.get(BASE_URL + "/health")
    print("[OK] Backend is running:", response.json())
except Exception as e:
    print("[ERROR] Backend error:", e)

# Test 2: Try to sign in with a known test user or create a new one
print("\nTrying to authenticate...")
try:
    # Try signing in with a test user
    signin_data = {
        "email": "admin@example.com",  # Common default user
        "password": "password123"
    }
    response = requests.post(BASE_URL + "/api/auth/signin", json=signin_data)
    if response.status_code == 200:
        result = response.json()
        print("[OK] User signed in successfully")
        token = result.get('access_token')
        user_id = result.get('user', {}).get('id')
        print(f"  - User ID: {user_id}")
        print(f"  - Token: {token[:20]}..." if token else "  - No token")
    else:
        print("[INFO] Default user not found, trying to create a new test user...")
        # Create a new test user
        signup_data = {
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
        response = requests.post(BASE_URL + "/api/auth/signup", json=signup_data)
        if response.status_code == 200:
            result = response.json()
            print("[OK] New test user created successfully")
            token = result.get('access_token')
            user_id = result.get('user', {}).get('id')
            print(f"  - User ID: {user_id}")
            print(f"  - Token: {token[:20]}..." if token else "  - No token")
        else:
            print("[ERROR] Failed to create test user:", response.status_code, response.text)
            token = None
            user_id = None
except Exception as e:
    print("[ERROR] Error during authentication:", e)
    token = None
    user_id = None

if token and user_id:
    # Test 3: Test chatbot functionality
    print(f"\nTesting chatbot with user {user_id}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Send a test message to add a task
        chat_data = {
            "message": "Add a task to buy groceries",
            "conversation_id": None
        }
        response = requests.post(f"{BASE_URL}/api/{user_id}/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("[OK] Chat message sent successfully")
            print(f"  - Response: {result.get('message', '')[:100]}...")
            conversation_id = result.get('conversation_id')
            print(f"  - Conversation ID: {conversation_id}")
        else:
            print("[ERROR] Chat message failed:", response.status_code, response.text)
    except Exception as e:
        print("[ERROR] Error during chat test:", e)

    # Test 4: Get user's tasks
    print(f"\nGetting tasks for user {user_id}...")
    try:
        response = requests.get(f"{BASE_URL}/api/tasks", headers=headers)
        if response.status_code == 200:
            tasks = response.json()
            print(f"[OK] Retrieved {len(tasks)} tasks")
            for task in tasks[-3:]:  # Show last 3 tasks
                print(f"  - Task {task.get('id')}: {task.get('title')} [{task.get('status', 'unknown')}]")
        else:
            print("[ERROR] Task retrieval failed:", response.status_code, response.text)
    except Exception as e:
        print("[ERROR] Error during task retrieval:", e)

print("\nTest completed!")