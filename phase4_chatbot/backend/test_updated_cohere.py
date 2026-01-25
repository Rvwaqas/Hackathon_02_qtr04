"""Test script to verify the updated Cohere client implementation."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.agents.cohere_client import get_cohere_agent_client

async def test_updated_cohere():
    """Test the updated Cohere client."""
    print("Testing Updated Cohere Client Implementation")
    print("=" * 50)

    # Get Cohere client
    client = get_cohere_agent_client()

    print(f"Model: {client.model}")
    print(f"Base URL: {client.base_url}")
    print(f"API Key Set: {'Yes' if client.api_key else 'No'}")

    if not client.api_key:
        print("\n[ERROR] COHERE_API_KEY not set!")
        print("Please set COHERE_API_KEY in your .env file")
        return

    print("\nSending test message to Cohere...")

    try:
        # Test the execute_agent method
        response = await client.execute_agent(
            user_message="Hello, how are you today?",
            conversation_history=[],
            system_prompt="You are a helpful assistant."
        )

        print(f"\n[SUCCESS] Response received:")
        print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")

        print("\n[SUCCESS] Updated Cohere client is working correctly!")

    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_updated_cohere())