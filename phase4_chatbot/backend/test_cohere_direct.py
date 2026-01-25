"""Direct test of Cohere API to verify connectivity and available models."""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_MODEL = os.getenv("COHERE_MODEL", "command-r-v4")
COHERE_BASE_URL = "https://api.cohere.com/v1"

async def test_cohere_direct():
    """Test Cohere API directly."""
    print(f"Testing Cohere API Connection")
    print(f"API Key: {COHERE_API_KEY[:20]}..." if COHERE_API_KEY else "NO API KEY")
    print(f"Model: {COHERE_MODEL}")
    print(f"Base URL: {COHERE_BASE_URL}")
    print()

    if not COHERE_API_KEY:
        print("ERROR: COHERE_API_KEY not set!")
        return

    # Initialize client
    client = AsyncOpenAI(
        api_key=COHERE_API_KEY,
        base_url=COHERE_BASE_URL
    )

    # Test simple message
    try:
        print("Sending test message to Cohere...")
        response = await client.chat.completions.create(
            model=COHERE_MODEL,
            messages=[
                {"role": "user", "content": "Say 'Hello, I work!' in one sentence."}
            ],
            temperature=0.7,
            max_tokens=100,
        )

        print("[SUCCESS] Cohere API is reachable")
        print(f"Response: {response.choices[0].message.content}")

    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        print(f"ERROR: {type(e).__name__}")
        print(f"Message: {error_msg}")
        print()

        # Try to extract more details
        if hasattr(e, 'response'):
            status = e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'
            body = e.response.text if hasattr(e.response, 'text') else 'Unknown'
            print(f"Status Code: {status}")
            print(f"Response Body: {body}")

        # Check if it's method not allowed
        if "405" in str(e):
            print()
            print("INFO: Got 405 Method Not Allowed. This suggests:")
            print("1. Cohere API endpoint may not support OpenAI-compatible format")
            print("2. Or AsyncOpenAI is not compatible with Cohere's endpoint")
            print()
            print("Trying alternative approaches...")

            # Try alternative models
            alt_models = ["command-r", "command-r-plus", "command-light", "command-nightly"]
            for model in alt_models:
                try:
                    print(f"  Trying {model}...", end=" ")
                    response = await client.chat.completions.create(
                        model=model,
                        messages=[{"role": "user", "content": "Hi"}],
                        max_tokens=10,
                    )
                    print(f" WORKS!")
                    return
                except Exception as e2:
                    error_msg2 = str(e2).encode('utf-8', errors='replace').decode('utf-8')
                    print(f" FAILED ({type(e2).__name__})")

if __name__ == "__main__":
    asyncio.run(test_cohere_direct())
