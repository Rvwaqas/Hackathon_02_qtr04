"""Test signin endpoint."""

import httpx

async def test_signin():
    """Test signin."""
    async with httpx.AsyncClient() as client:
        # First signup
        print("Creating test user...")
        signup_response = await client.post(
            "http://localhost:8000/api/auth/signup",
            json={
                "name": "Test User",
                "email": "testuser_signin@test.com",
                "password": "TestPassword123!"
            }
        )
        print(f"Signup Status: {signup_response.status_code}")

        if signup_response.status_code != 201:
            print(f"Signup failed: {signup_response.json()}")
            return

        # Now try signin
        print("\nTesting signin...")
        signin_response = await client.post(
            "http://localhost:8000/api/auth/signin",
            json={
                "email": "testuser_signin@test.com",
                "password": "TestPassword123!"
            }
        )

        print(f"Signin Status: {signin_response.status_code}")
        print(f"Signin Response: {signin_response.json()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_signin())
