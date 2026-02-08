"""Direct test of Gemini API via OpenAI SDK."""

import asyncio
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

# Load environment
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"

async def test_gemini_direct():
    """Test Gemini API directly via AsyncOpenAI."""
    print("Testing Gemini API Connection (OpenAI-compatible endpoint)")
    print(f"API Key: {GEMINI_API_KEY[:20]}..." if GEMINI_API_KEY else "NO API KEY")
    print(f"Model: {GEMINI_MODEL}")
    print(f"Base URL: {GEMINI_BASE_URL}")
    print()

    if not GEMINI_API_KEY:
        print("ERROR: GEMINI_API_KEY not set!")
        return

    # Initialize client
    client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url=GEMINI_BASE_URL
    )

    # Test simple message
    try:
        print("Sending test message to Gemini...")
        response = await client.chat.completions.create(
            model=GEMINI_MODEL,
            messages=[
                {"role": "user", "content": "Say 'Hello, Gemini is working!' in one sentence."}
            ],
            temperature=0.7,
            max_tokens=100,
        )

        print("SUCCESS! Gemini API is reachable via OpenAI SDK")
        print(f"Response: {response.choices[0].message.content}")
        return True

    except Exception as e:
        error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
        print(f"ERROR: {type(e).__name__}")
        print(f"Message: {error_msg}")

        if hasattr(e, 'response'):
            status = e.response.status_code if hasattr(e.response, 'status_code') else 'Unknown'
            print(f"Status Code: {status}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_gemini_direct())
    if not success:
        print("\nGemini API test failed. Checking alternative models...")
