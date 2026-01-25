import requests
import json
import time

# Test the full application flow with a unique user
BASE_URL = "http://localhost:8000"

print("Testing TaskFlow Application...")

# Test 1: Check backend
try:
    response = requests.get(BASE_URL + "/health")
    print("[OK] Backend is running:", response.json())
except Exception as e:
    print("[ERROR] Backend error:", e)

# Test 2: Create a unique test user
print("\nCreating unique test user...")
unique_email = f"test_{int(time.time())}@example.com"
print(f"Using email: {unique_email}")

try:
    signup_data = {
        "name": "Test User",
        "email": unique_email,
        "password": "testpassword123"
    }
    response = requests.post(BASE_URL + "/api/auth/signup", json=signup_data)
    if response.status_code in [200, 201]:  # 200 OK or 201 Created
        result = response.json()
        print("[OK] User created successfully")
        token = result.get('access_token')
        user_id = result.get('user', {}).get('id')
        print(f"  - User ID: {user_id}")
        print(f"  - Token: {token[:20]}..." if token else "  - No token")
    else:
        print("[ERROR] User creation failed:", response.status_code, response.text)
        token = None
        user_id = None
except Exception as e:
    print("[ERROR] Error during user creation:", e)
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

    # Test 5: Test another chat command
    print(f"\nTesting another chat command...")
    try:
        chat_data = {
            "message": "Show my tasks",
            "conversation_id": conversation_id  # Use the conversation we just created
        }
        response = requests.post(f"{BASE_URL}/api/{user_id}/chat", json=chat_data, headers=headers)
        if response.status_code == 200:
            result = response.json()
            print("[OK] Second chat message sent successfully")
            print(f"  - Response: {result.get('message', '')[:100]}...")
        else:
            print("[ERROR] Second chat message failed:", response.status_code, response.text)
    except Exception as e:
        print("[ERROR] Error during second chat test:", e)

print("\nTest completed!")