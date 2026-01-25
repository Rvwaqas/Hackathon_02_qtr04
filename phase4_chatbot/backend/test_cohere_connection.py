"""Test script to verify Cohere API connection."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Cohere client
from src.agents.cohere_client import CohereAgentClient

async def test_cohere_connection():
    """Test Cohere API connection."""
    try:
        print("Testing Cohere API connection...")
        
        # Create client instance
        client = CohereAgentClient()
        
        print(f"Model: {client.model}")
        print(f"Base URL: {client.base_url}")
        print(f"API Key present: {'Yes' if client.api_key else 'No'}")
        
        # Test a simple chat request
        print("\nTesting chat request...")
        response = await client.execute_agent(
            user_message="Hello, how are you?",
            conversation_history=[],
            system_prompt="You are a helpful assistant."
        )
        
        print(f"Response received: {response[:100]}...")
        print("[SUCCESS] Cohere API connection successful!")

    except Exception as e:
        print(f"[ERROR] Error connecting to Cohere API: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cohere_connection())