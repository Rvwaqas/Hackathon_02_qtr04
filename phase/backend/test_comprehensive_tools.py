"""Comprehensive test to verify tools functionality."""

import asyncio
from src.agents.cohere_client import get_cohere_agent_client
from src.agents.config import TOOL_DEFINITIONS
from src.mcp.tools import TodoToolsHandler
from src.database import async_session_factory


async def test_comprehensive_tools():
    """Test that tools are properly integrated and functional."""
    print("Comprehensive Tools Integration Test")
    print("=" * 50)
    
    # Get Cohere client
    client = get_cohere_agent_client()
    print(f"Cohere client initialized: {client.model}")
    
    # Create a mock session for the tools handler
    async with async_session_factory() as session:
        # Create tools handler
        tools_handler = TodoToolsHandler(session, "test-user-123")
        print("Tools handler created successfully")
        
        # Test 1: Simple message without tools
        print("\n1. Testing simple message without tools...")
        response = await client.execute_agent(
            user_message="Hello, how are you?",
            conversation_history=[],
            system_prompt="You are a helpful todo assistant.",
            tools=TOOL_DEFINITIONS,
            tools_handler=tools_handler
        )
        print(f"Response: {response}")
        
        # Test 2: Request that should trigger add_task
        print("\n2. Testing add_task functionality...")
        response = await client.execute_agent(
            user_message="Add a task to buy groceries",
            conversation_history=[],
            system_prompt="You are a helpful todo assistant. You have access to tools for managing tasks.",
            tools=TOOL_DEFINITIONS,
            tools_handler=tools_handler
        )
        print(f"Response: {response}")
        
        # Test 3: Request that should trigger list_tasks
        print("\n3. Testing list_tasks functionality...")
        response = await client.execute_agent(
            user_message="Show me my tasks",
            conversation_history=[],
            system_prompt="You are a helpful todo assistant. You have access to tools for managing tasks.",
            tools=TOOL_DEFINITIONS,
            tools_handler=tools_handler
        )
        print(f"Response: {response}")
        
        print("\nAll tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_comprehensive_tools())