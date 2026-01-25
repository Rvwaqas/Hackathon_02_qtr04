"""Test chat response to verify conversation_id and message."""

import httpx
import json
from datetime import datetime

async def test_chat_response():
    """Test chat endpoint response."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Create unique user
        timestamp = datetime.now().timestamp()
        email = f"testuser_{timestamp}@test.com"

        print(f"Creating user: {email}")

        # Signup
        signup_response = await client.post(
            "http://localhost:8000/api/auth/signup",
            json={
                "name": "Test User",
                "email": email,
                "password": "TestPassword123!"
            }
        )

        if signup_response.status_code != 201:
            print(f"Signup failed: {signup_response.json()}")
            return

        signup_data = signup_response.json()
        user_id = signup_data["user"]["id"]
        token = signup_data["access_token"]

        print(f"User created: {user_id}")
        print(f"Token: {token[:30]}...")
        print()

        # Chat
        print("Sending chat message...")
        chat_response = await client.post(
            f"http://localhost:8000/api/{user_id}/chat",
            json={"message": "hi"},
            headers={"Authorization": f"bearer {token}"},
            timeout=60.0
        )

        print(f"Status: {chat_response.status_code}")
        print(f"Full Response:")
        print(json.dumps(chat_response.json(), indent=2))

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_chat_response())
