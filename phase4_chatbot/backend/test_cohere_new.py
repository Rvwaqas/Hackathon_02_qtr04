"""Test Cohere API with new key and base URL."""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_BASE_URL = os.getenv("COHERE_BASE_URL", "https://api.cohere.ai")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-plus")

async def test_cohere():
    """Test Cohere API."""
    print("Testing Cohere API")
    print(f"API Key: {COHERE_API_KEY[:20]}...")
    print(f"Base URL: {COHERE_BASE_URL}")
    print(f"Model: {COHERE_MODEL}")
    print()

    try:
        import cohere
    except ImportError:
        print("Installing cohere SDK...")
        os.system("pip install cohere -q")
        import cohere

    try:
        print("Initializing Cohere client...")
        client = cohere.AsyncClientV2(
            api_key=COHERE_API_KEY,
            base_url=COHERE_BASE_URL
        )

        print("Sending test message...")
        response = await client.chat(
            model=COHERE_MODEL,
            messages=[
                {"role": "user", "content": "Say hello in one sentence."}
            ],
            temperature=0.7,
            max_tokens=100,
        )

        print("SUCCESS! Cohere API is working")
        print(f"Response: {response.message.content[0].text if response.message.content else 'No content'}")

    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        print(f"ERROR: {type(e).__name__}")
        print(f"Message: {error_msg}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_cohere())
