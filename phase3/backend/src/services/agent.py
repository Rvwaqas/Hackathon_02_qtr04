"""AI Agent service using Cohere via OpenAI-compatible client."""

import json
import os
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.mcp.tools import (
    add_task,
    list_tasks,
    complete_task,
    update_task,
    delete_task,
    get_mcp_tools
)

# System prompt for the todo assistant
SYSTEM_PROMPT = """You are a friendly todo assistant. Help users manage their tasks using natural language.

When to use each tool:
- add_task: When user wants to create, add, or remind about something
- list_tasks: When user asks to show, list, see, or view tasks
- complete_task: When user says done, complete, finish, mark done
- update_task: When user says change, rename, update, modify
- delete_task: When user says delete, remove, cancel

Always:
- Confirm actions with friendly messages
- Include task titles in confirmations
- Ask for clarification if the request is ambiguous
- Show available tasks if referenced task not found
- Be concise but helpful

When listing tasks, format them nicely with IDs so users can reference them.
"""


class AgentService:
    """Service for managing AI agent interactions."""

    def __init__(self):
        """Initialize the Cohere client via OpenAI-compatible API."""
        api_key = settings.COHERE_API_KEY or os.getenv("COHERE_API_KEY")

        if not api_key:
            raise ValueError("COHERE_API_KEY is required")

        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url="https://api.cohere.com/v1"
        )
        self.model = "command-r-plus"
        self.tools = get_mcp_tools()

    async def _execute_tool(
        self,
        session: AsyncSession,
        user_id: int,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an MCP tool and return the result.

        Args:
            session: Database session
            user_id: User ID for tool context
            tool_name: Name of the tool to execute
            arguments: Tool arguments

        Returns:
            Tool execution result
        """
        tool_functions = {
            "add_task": add_task,
            "list_tasks": list_tasks,
            "complete_task": complete_task,
            "update_task": update_task,
            "delete_task": delete_task
        }

        tool_func = tool_functions.get(tool_name)
        if not tool_func:
            return {"success": False, "error": f"Unknown tool: {tool_name}"}

        try:
            result = await tool_func(session=session, user_id=user_id, **arguments)
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def chat(
        self,
        session: AsyncSession,
        user_id: int,
        message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return the response.

        Args:
            session: Database session
            user_id: User ID for tool context
            message: User's message
            history: Previous conversation messages

        Returns:
            Dict with response text and tool calls
        """
        # Build messages array
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add history if provided
        if history:
            messages.extend(history)

        # Add current user message
        messages.append({"role": "user", "content": message})

        tool_calls_made = []
        max_iterations = 5  # Prevent infinite loops

        for _ in range(max_iterations):
            try:
                # Call Cohere via OpenAI-compatible API
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools if self.tools else None,
                    tool_choice="auto" if self.tools else None
                )

                assistant_message = response.choices[0].message

                # Check if we need to execute tools
                if assistant_message.tool_calls:
                    # Add assistant message with tool calls to history
                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content or "",
                        "tool_calls": [
                            {
                                "id": tc.id,
                                "type": "function",
                                "function": {
                                    "name": tc.function.name,
                                    "arguments": tc.function.arguments
                                }
                            }
                            for tc in assistant_message.tool_calls
                        ]
                    })

                    # Execute each tool call
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}

                        # Execute the tool
                        result = await self._execute_tool(
                            session=session,
                            user_id=user_id,
                            tool_name=tool_name,
                            arguments=arguments
                        )

                        tool_calls_made.append({
                            "tool": tool_name,
                            "arguments": arguments,
                            "result": result
                        })

                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })

                    # Continue loop to get final response
                    continue

                # No tool calls, return the response
                return {
                    "response": assistant_message.content or "I'm here to help with your tasks!",
                    "tool_calls": tool_calls_made
                }

            except Exception as e:
                # Handle API errors gracefully
                error_msg = str(e)
                if "rate_limit" in error_msg.lower():
                    return {
                        "response": "I'm a bit busy right now. Please try again in a moment.",
                        "tool_calls": tool_calls_made,
                        "error": error_msg
                    }
                elif "api_key" in error_msg.lower() or "authentication" in error_msg.lower():
                    return {
                        "response": "There's an issue with the AI service configuration. Please try again later.",
                        "tool_calls": tool_calls_made,
                        "error": error_msg
                    }
                else:
                    return {
                        "response": "Something went wrong. Please try again.",
                        "tool_calls": tool_calls_made,
                        "error": error_msg
                    }

        # Max iterations reached
        return {
            "response": "I had trouble processing your request. Please try again with a simpler command.",
            "tool_calls": tool_calls_made
        }


# Global agent instance (lazy initialization)
_agent_instance: Optional[AgentService] = None


def get_agent() -> AgentService:
    """
    Get or create the global agent instance.

    Returns:
        AgentService: The agent service instance
    """
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentService()
    return _agent_instance
