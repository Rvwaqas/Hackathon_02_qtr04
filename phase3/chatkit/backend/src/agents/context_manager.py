"""ContextManager agent - Manages conversation history and context."""

from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.conversation import ConversationService
from src.models.message import Message


class ContextManager:
    """
    Agent responsible for managing conversation history.

    Responsibilities:
    - Load last N messages from conversation
    - Save new messages after response
    - Track conversation_id
    - Limit token usage by capping message history
    """

    def __init__(self, session: AsyncSession):
        """Initialize the ContextManager agent."""
        self.session = session
        self.conversation_service = ConversationService()

    async def load_history(
        self,
        conversation_id: Optional[int],
        user_id: int,
        limit: int = 20
    ) -> tuple[int, List[Message]]:
        """
        Load conversation history.

        Args:
            conversation_id: Conversation ID (None to create new)
            user_id: User ID
            limit: Maximum number of messages to load

        Returns:
            Tuple of (conversation_id, list of messages)
        """
        # Create new conversation if needed
        if conversation_id is None:
            conversation = await self.conversation_service.create_conversation(
                session=self.session,
                user_id=user_id,
                title="New Conversation"
            )
            return conversation.id, []

        # Validate conversation ownership
        conversation = await self.conversation_service.get_conversation(
            session=self.session,
            conversation_id=conversation_id,
            user_id=user_id
        )

        if not conversation:
            # Conversation not found or not owned by user
            # Create new conversation
            conversation = await self.conversation_service.create_conversation(
                session=self.session,
                user_id=user_id,
                title="New Conversation"
            )
            return conversation.id, []

        # Load messages
        messages = await self.conversation_service.get_messages(
            session=self.session,
            conversation_id=conversation_id,
            limit=limit
        )

        return conversation_id, messages

    async def save_message(
        self,
        conversation_id: int,
        role: str,
        content: str,
        tool_calls: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Message:
        """
        Save a message to the conversation.

        Args:
            conversation_id: Conversation ID
            role: Message role ("user" or "assistant")
            content: Message content
            tool_calls: List of tool names that were called
            metadata: Additional metadata

        Returns:
            Saved message
        """
        return await self.conversation_service.add_message(
            session=self.session,
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            metadata=metadata
        )

    @staticmethod
    def format_messages_for_context(messages: List[Message]) -> str:
        """
        Format messages into a context string for the LLM.

        Args:
            messages: List of messages

        Returns:
            Formatted context string
        """
        if not messages:
            return "This is a new conversation."

        context_lines = ["Recent conversation history:"]
        for msg in messages:
            role_indicator = "User" if msg.role == "user" else "Assistant"
            context_lines.append(f"{role_indicator}: {msg.content}")

        return "\n".join(context_lines)
