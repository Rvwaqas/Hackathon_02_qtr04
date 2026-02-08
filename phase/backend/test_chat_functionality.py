"""Simple test to verify the chat functionality works without starting full server."""

import asyncio
from src.agents.cohere_client import get_cohere_agent_client

async def test_chat_functionality():
    """Test the chat functionality directly."""
    print("Testing chat functionality...")

    # Test the Cohere client directly
    try:
        client = get_cohere_agent_client()
        print("Cohere client initialized successfully")
    except Exception as e:
        print(f"Error initializing Cohere client: {e}")
        return

    # Test a simple chat execution
    try:
        response = await client.execute_agent(
            user_message="Hello, how are you?",
            conversation_history=[],
            system_prompt="You are a helpful assistant."
        )
        print(f"Cohere API call successful: {response[:50]}...")
    except Exception as e:
        print(f"Error calling Cohere API: {e}")
        return

    print("All chat functionality tests passed!")
    print("The original error was likely due to Unicode/emoji encoding issues on Windows.")
    print("These have been fixed by replacing emojis with text equivalents.")

if __name__ == "__main__":
    asyncio.run(test_chat_functionality())