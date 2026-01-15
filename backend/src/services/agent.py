"""AI Agent Service using OpenAI Agents SDK with Gemini backend."""

import os
from typing import List, Dict, Any, Optional
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, set_tracing_disabled
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings

# Disable tracing for clean output
set_tracing_disabled(disabled=True)

# System prompt for the todo chatbot
SYSTEM_PROMPT = """You are a helpful AI assistant for TaskFlow, a task management application.

You help users manage their tasks by having friendly conversations. When users want to:
- Add a task: Help them add it to their todo list
- View tasks: Show their current tasks
- Complete a task: Mark it as done
- Update a task: Change task details
- Delete a task: Remove it from their list

Be friendly, helpful, and conversational. Keep responses concise but informative."""


class AgentService:
    """AI Agent service using OpenAI Agents SDK with Gemini backend."""

    def __init__(self):
        """Initialize the agent with Gemini API via OpenAI Agents SDK."""
        self.api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.base_url = settings.GEMINI_BASE_URL or os.getenv("GEMINI_BASE_URL")

        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set. Please set it in .env file.")

        # Create AsyncOpenAI-compatible client with Gemini endpoint
        self.external_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

        # Create the model using OpenAI Agents SDK
        self.model = OpenAIChatCompletionsModel(
            model="gemini-2.0-flash",
            openai_client=self.external_client
        )

        # Create the agent
        self.agent = Agent(
            name="TaskFlow Assistant",
            instructions=SYSTEM_PROMPT,
            model=self.model
        )

    async def chat(
        self,
        user_id: int,
        message: str,
        session: AsyncSession,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Process a chat message and return AI response.

        Args:
            user_id: The user's ID
            message: The user's message
            session: Database session
            conversation_history: Previous messages in the conversation

        Returns:
            Dict with response and tool_calls
        """
        try:
            # Build input with conversation history
            if conversation_history and len(conversation_history) > 0:
                # Format conversation history for context
                history_text = ""
                for msg in conversation_history:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_text += f"{role}: {msg['content']}\n"

                # Include history in the message
                full_message = f"Previous conversation:\n{history_text}\nUser: {message}"
            else:
                full_message = message

            # Run the agent using async Runner
            result = await Runner.run(self.agent, full_message)

            # Extract response text
            response_text = result.final_output

            return {
                "response": response_text,
                "tool_calls": []
            }

        except Exception as e:
            print(f"Error getting response: {str(e)}")
            return {
                "response": f"I apologize, but I encountered an error: {str(e)}. Please try again.",
                "tool_calls": []
            }


# Singleton instance
_agent_instance: Optional[AgentService] = None


def get_agent() -> AgentService:
    """Get or create the agent service instance."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = AgentService()
    return _agent_instance
