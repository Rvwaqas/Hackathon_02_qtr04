"""Test login and chat with provided credentials."""

import httpx
import json
import asyncio

async def test_login_and_chat():
    """Test login and send chat message."""

    async with httpx.AsyncClient(timeout=60.0) as client:
        email = "rvwaqas602@gmail.com"
        password = "12345678"

        print("=" * 60)
        print("TESTING CHATBOT WITH PROVIDED CREDENTIALS")
        print("=" * 60)
        print()

        # 1. Try to login
        print(f"[1] Attempting login with {email}...")

        login_response = await client.post(
            "http://localhost:8000/api/auth/signin",
            json={"email": email, "password": password},
            timeout=30.0
        )

        print(f"    Status: {login_response.status_code}")

        if login_response.status_code == 200:
            login_data = login_response.json()
            user_id = login_data["user"]["id"]
            token = login_data["access_token"]
            print(f"    SUCCESS: Logged in as user {user_id}")
            print()
        else:
            print(f"    ERROR: {login_response.json()}")
            print("\n    Attempting signup instead...")

            signup_response = await client.post(
                "http://localhost:8000/api/auth/signup",
                json={
                    "name": "Waqas",
                    "email": email,
                    "password": password
                },
                timeout=30.0
            )

            if signup_response.status_code == 201:
                signup_data = signup_response.json()
                user_id = signup_data["user"]["id"]
                token = signup_data["access_token"]
                print(f"    SUCCESS: Signed up as user {user_id}")
                print()
            else:
                print(f"    ERROR: Signup failed - {signup_response.json()}")
                return

        # 2. Send chat message
        print(f"[2] Sending chat message: 'add task: buy groceries'")

        chat_response = await client.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "add task: buy groceries"},
            headers={"Authorization": f"bearer {token}"},
            timeout=60.0
        )

        print(f"    Status: {chat_response.status_code}")

        if chat_response.status_code == 200:
            chat_data = chat_response.json()
            print(f"    SUCCESS: Got response from chatbot")
            print(f"    Conversation ID: {chat_data.get('conversation_id')}")
            print(f"    Response: {chat_data.get('message')}")
            print()

            # 3. Get conversation history
            conv_id = chat_data.get('conversation_id')
            if conv_id:
                print(f"[3] Retrieving conversation history...")
                history_response = await client.get(
                    f"http://localhost:8000/api/{user_id}/conversations/{conv_id}",
                    headers={"Authorization": f"bearer {token}"},
                    timeout=30.0
                )

                if history_response.status_code == 200:
                    history_data = history_response.json()
                    print(f"    SUCCESS: Retrieved conversation")
                    print(f"    Messages ({len(history_data['messages'])}):")
                    for msg in history_data['messages']:
                        print(f"      - {msg['role']}: {msg['content'][:60]}...")
                else:
                    print(f"    ERROR: {history_response.json()}")
        else:
            print(f"    ERROR: {chat_response.json()}")

        print()
        print("=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_login_and_chat())
