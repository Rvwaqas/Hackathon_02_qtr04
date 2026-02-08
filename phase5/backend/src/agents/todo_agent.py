"""TodoAgent: Uses OpenAI Agents SDK with Cohere for task management."""

from typing import Optional, List, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from src.agents.cohere_client import get_cohere_agent_client
from src.agents.config import SYSTEM_PROMPT, TOOL_DEFINITIONS


class TodoAgent:
    """Agent that uses OpenAI Agents SDK with Cohere for task management."""

    def __init__(
        self,
        session: AsyncSession,
        user_id: str,
    ):
        """Initialize TodoAgent.

        Args:
            session: SQLAlchemy async database session
            user_id: Authenticated user ID (from JWT)
        """
        self.session = session
        self.user_id = user_id
        self.cohere_client = get_cohere_agent_client()

    async def execute(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Execute agent with user message.

        Args:
            user_message: User's natural language request
            conversation_history: List of {role, content} dicts for context
            temperature: Optional override for model temperature
            max_tokens: Optional override for max response tokens

        Returns:
            Agent's response text
        """
        try:
            # Get system prompt from config
            system_prompt = SYSTEM_PROMPT

            # Get tool definitions from config
            tools = TOOL_DEFINITIONS

            # Import the tools handler
            from src.mcp import TodoToolsHandler
            tools_handler = TodoToolsHandler(self.session, self.user_id)

            # Execute agent using Cohere with OpenAI Agents SDK
            response = await self.cohere_client.execute_agent(
                user_message=user_message,
                conversation_history=conversation_history,
                system_prompt=system_prompt,
                tools=tools,
                tools_handler=tools_handler
            )

            return response if response else "I couldn't process that request. Please try again."

        except Exception as e:
            error_msg = str(e).encode('utf-8', errors='replace').decode('utf-8')
            print(f"[ERROR] TodoAgent execution failed: {error_msg}".encode('utf-8', errors='replace').decode('utf-8'))
            print(f"[DEBUG] Exception type: {type(e).__name__}".encode('utf-8', errors='replace').decode('utf-8'))
            print(f"[DEBUG] Full exception: {repr(e)}".encode('utf-8', errors='replace').decode('utf-8'))
            import traceback
            print("[DEBUG] Traceback:".encode('utf-8', errors='replace').decode('utf-8'))
            traceback.print_exc()
            # Return user-friendly error message
            return f"Sorry, I encountered an error processing your request. Please try again later."
