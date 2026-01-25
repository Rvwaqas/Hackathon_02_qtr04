"""Test using official Cohere SDK to verify API key and models."""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

COHERE_API_KEY = os.getenv("COHERE_API_KEY")

async def test_official_cohere():
    """Test with official Cohere SDK."""
    if not COHERE_API_KEY:
        print("ERROR: COHERE_API_KEY not set!")
        return

    try:
        import cohere
    except ImportError:
        print("Installing cohere SDK...")
        os.system("pip install cohere -q")
        import cohere

    print("Testing with Official Cohere SDK")
    print(f"API Key: {COHERE_API_KEY[:20]}...")
    print()

    # Initialize Cohere client
    client = cohere.AsyncClientV2(api_key=COHERE_API_KEY)

    try:
        print("Sending test message...")
        response = await client.chat(
            model="command-r-v4",
            messages=[
                {
                    "role": "user",
                    "content": "Say hello in one sentence.",
                }
            ],
        )

        print("SUCCESS! Cohere API is working")
        print(f"Response: {response.message.content[0].text}")

    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        print(f"ERROR: {type(e).__name__}")
        print(f"Message: {error_msg}")

        # Try alternate model
        print()
        print("Trying alternate models...")

        alt_models = ["command-r", "command-r-plus", "command-light", "command-nightly"]
        for model in alt_models:
            try:
                print(f"  Trying {model}...", end=" ")
                response = await client.chat(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                )
                print(f" WORKS!")
                return
            except Exception as e2:
                error_msg2 = str(e2).encode('utf-8', errors='replace').decode('utf-8')
                print(f" FAILED ({type(e2).__name__})")

if __name__ == "__main__":
    asyncio.run(test_official_cohere())
