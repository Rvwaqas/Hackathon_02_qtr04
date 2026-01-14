"""Conversation service for AI chatbot."""

from sqlmodel import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import List, Optional, Dict

from src.models import Conversation, Message


class ConversationService:
    """Service for managing conversations and messages."""

    @classmethod
    async def get_or_create_conversation(
        cls, session: AsyncSession, user_id: int, conversation_id: Optional[str] = None
    ) -> Conversation:
        """
        Get existing conversation or create a new one.

        Args:
            session: Database session
            user_id: User ID
            conversation_id: Optional specific conversation ID

        Returns:
            Conversation: The conversation object
        """
        if conversation_id:
            # Try to find specific conversation
            result = await session.execute(
                select(Conversation).where(
                    Conversation.id == conversation_id,
                    Conversation.user_id == user_id
                )
            )
            conversation = result.scalar_one_or_none()
            if conversation:
                return conversation

        # Find most recent conversation for user
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(1)
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            return conversation

        # Create new conversation
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        await session.commit()
        await session.refresh(conversation)
        return conversation

    @classmethod
    async def load_history(
        cls,
        session: AsyncSession,
        conversation_id: str,
        user_id: int,
        limit: int = 20
    ) -> List[Dict]:
        """
        Load message history for a conversation.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID for data isolation
            limit: Maximum number of messages to return

        Returns:
            List of message dicts in chronological order
        """
        result = await session.execute(
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = result.scalars().all()

        # Reverse to chronological order and format for agent
        return [
            {"role": m.role, "content": m.content}
            for m in reversed(messages)
        ]

    @classmethod
    async def save_message(
        cls,
        session: AsyncSession,
        conversation_id: str,
        user_id: int,
        role: str,
        content: str,
        tool_call_id: Optional[str] = None,
        tool_name: Optional[str] = None
    ) -> Message:
        """
        Save a message to the conversation.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID
            role: Message role (user, assistant, tool, system)
            content: Message content
            tool_call_id: Optional tool call ID
            tool_name: Optional tool name

        Returns:
            Message: The saved message
        """
        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_call_id=tool_call_id,
            tool_name=tool_name
        )
        session.add(message)

        # Update conversation timestamp
        await session.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=datetime.utcnow())
        )

        await session.commit()
        await session.refresh(message)
        return message

    @classmethod
    async def update_conversation_title(
        cls,
        session: AsyncSession,
        conversation_id: str,
        user_id: int,
        title: str
    ) -> Optional[Conversation]:
        """
        Update conversation title.

        Args:
            session: Database session
            conversation_id: Conversation ID
            user_id: User ID for ownership check
            title: New title

        Returns:
            Conversation or None if not found
        """
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            return None

        conversation.title = title[:200] if title else None
        conversation.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(conversation)
        return conversation
