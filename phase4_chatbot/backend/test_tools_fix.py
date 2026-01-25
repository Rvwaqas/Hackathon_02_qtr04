"""Test script to verify the tools fix is working."""

import asyncio
import json
from src.agents.cohere_client import get_cohere_agent_client
from src.agents.config import TOOL_DEFINITIONS
from src.mcp.tools import TodoToolsHandler
from src.database import get_session, async_session_factory
from sqlalchemy.ext.asyncio import AsyncSession


async def test_tools_fix():
    """Test that the tools are properly integrated."""
    print("Testing Tools Integration Fix")
    print("=" * 40)

    # Get Cohere client
    client = get_cohere_agent_client()
    print(f"Cohere client initialized: {client.model}")

    # Check if tools are defined
    print(f"Number of tools defined: {len(TOOL_DEFINITIONS)}")
    for tool in TOOL_DEFINITIONS:
        print(f"  - {tool['name']}: {tool['description']}")

    # Test a simple message to see if tools are recognized
    print("\nTesting simple message...")
    try:
        # Create a mock session for the tools handler
        async with async_session_factory() as session:
            # Create tools handler
            tools_handler = TodoToolsHandler(session, "test-user-123")
            print("Tools handler created successfully")

            # Test the execute_agent method with tools
            response = await client.execute_agent(
                user_message="What can you help me with?",
                conversation_history=[],
                system_prompt="You are a helpful todo assistant. You have access to tools for managing tasks.",
                tools=TOOL_DEFINITIONS,
                tools_handler=tools_handler
            )

            print(f"Response: {response}")

    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_tools_fix())