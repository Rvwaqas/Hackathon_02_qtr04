"""OpenAI configuration for agents."""

import os
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

# OpenAI configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable is required")


def get_openai_client() -> AsyncOpenAI:
    """
    Get configured OpenAI client.

    Returns:
        AsyncOpenAI: Configured OpenAI client
    """
    return AsyncOpenAI(api_key=OPENAI_API_KEY)
