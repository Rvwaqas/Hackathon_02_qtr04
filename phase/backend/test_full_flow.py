"""Comprehensive test of full chatbot flow: signup -> login -> chat."""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_full_flow():
    """Test complete chatbot flow."""
    print("=" * 60)
    print("FULL CHATBOT FLOW TEST")
    print("=" * 60)
    print()

    async with httpx.AsyncClient(timeout=30.0) as client:
        # 1. Signup
        print("[1] Testing User Signup...")
        signup_payload = {
            "name": "Test User",
            "email": f"testuser_{datetime.now().timestamp()}@test.com",
            "password": "TestPassword123!"
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/signup",
                json=signup_payload
            )

            if response.status_code == 201:
                signup_data = response.json()
                user_id = signup_data.get("user", {}).get("id")
                print(f"   SUCCESS: User created with ID: {user_id}")
                print(f"   Email: {signup_payload['email']}")
            else:
                print(f"   ERROR: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"   ERROR: {type(e).__name__}: {str(e)}")
            return

        print()

        # 2. Login
        print("[2] Testing User Login...")
        login_payload = {
            "email": signup_payload["email"],
            "password": signup_payload["password"]
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/signin",
                json=login_payload
            )

            if response.status_code == 200:
                login_data = response.json()
                token = login_data.get("access_token")
                token_type = login_data.get("token_type")
                print(f"   SUCCESS: Logged in successfully")
                print(f"   Token Type: {token_type}")
                print(f"   Token: {token[:50]}...")
            else:
                print(f"   ERROR: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return
        except Exception as e:
            print(f"   ERROR: {type(e).__name__}: {str(e)}")
            return

        print()

        # 3. Chat - Create conversation and send message
        print("[3] Testing Chat Endpoint...")

        headers = {
            "Authorization": f"{token_type} {token}"
        }

        chat_payload = {
            "message": "Hello! Can you help me create a todo list?"
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/{user_id}/chat",
                json=chat_payload,
                headers=headers,
                timeout=60.0
            )

            print(f"   Status Code: {response.status_code}")

            if response.status_code == 200:
                chat_data = response.json()
                print(f"   SUCCESS: Chat response received")
                print(f"   Conversation ID: {chat_data.get('conversation_id')}")
                print(f"   Response Message:")
                print(f"   {chat_data.get('message')}")
                conversation_id = chat_data.get('conversation_id')
            else:
                print(f"   ERROR: Status {response.status_code}")
                print(f"   Response: {response.text}")
                return

        except httpx.TimeoutException:
            print(f"   ERROR: Request timeout (60s) - Gemini API may be unresponsive or quota exhausted")
            return
        except Exception as e:
            print(f"   ERROR: {type(e).__name__}: {str(e)}")
            return

        print()

        # 4. Get conversations list
        print("[4] Testing Get Conversations List...")

        try:
            response = await client.get(
                f"{BASE_URL}/api/{user_id}/conversations",
                headers=headers
            )

            if response.status_code == 200:
                conversations = response.json()
                print(f"   SUCCESS: Retrieved {len(conversations)} conversation(s)")
                for conv in conversations:
                    print(f"   - {conv.get('id')}: {conv.get('title') or 'Untitled'}")
            else:
                print(f"   ERROR: Status {response.status_code}")
                print(f"   Response: {response.text}")

        except Exception as e:
            print(f"   ERROR: {type(e).__name__}: {str(e)}")

        print()

        # 5. Get conversation details
        if conversation_id:
            print("[5] Testing Get Conversation Details...")

            try:
                response = await client.get(
                    f"{BASE_URL}/api/{user_id}/conversations/{conversation_id}",
                    headers=headers
                )

                if response.status_code == 200:
                    conv_detail = response.json()
                    messages = conv_detail.get('messages', [])
                    print(f"   SUCCESS: Retrieved conversation details")
                    print(f"   Title: {conv_detail.get('title') or 'Untitled'}")
                    print(f"   Messages ({len(messages)}):")
                    for msg in messages:
                        print(f"   - {msg['role']}: {msg['content'][:60]}...")
                else:
                    print(f"   ERROR: Status {response.status_code}")
                    print(f"   Response: {response.text}")

            except Exception as e:
                print(f"   ERROR: {type(e).__name__}: {str(e)}")

        print()
        print("=" * 60)
        print("TEST COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    asyncio.run(test_full_flow())
