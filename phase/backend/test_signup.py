"""Test signup endpoint."""

import httpx
import json

async def test_signup():
    """Test signup."""
    async with httpx.AsyncClient() as client:
        payload = {
            "name": "Test User",
            "email": f"testuser{id(object())}@test.com",
            "password": "TestPassword123!"
        }

        print(f"Payload: {json.dumps(payload)}")
        print()

        response = await client.post(
            "http://localhost:8000/api/auth/signup",
            json=payload
        )

        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_signup())
