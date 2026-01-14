# Manage Conversation DB

Handle stateless conversation persistence with SQLModel and Neon PostgreSQL.

## Database Models

```python
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime
from typing import Optional
import uuid

class Conversation(SQLModel, table=True):
    """Conversation session for a user."""

    __tablename__ = "conversations"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True)  # From JWT
    title: Optional[str] = None  # Auto-generated from first message
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    messages: list["Message"] = Relationship(back_populates="conversation")

    # Composite index for fast lookup
    __table_args__ = (
        Index("idx_conversation_user_id", "user_id"),
    )


class Message(SQLModel, table=True):
    """Individual message in a conversation."""

    __tablename__ = "messages"

    id: int = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversations.id", index=True)
    user_id: str = Field(index=True)  # Denormalized for fast queries
    role: str  # "user", "assistant", "tool", "system"
    content: str
    tool_call_id: Optional[str] = None  # For tool responses
    tool_name: Optional[str] = None  # Name of tool called
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    conversation: Optional[Conversation] = Relationship(back_populates="messages")

    # Composite index for conversation history queries
    __table_args__ = (
        Index("idx_message_conv_user", "conversation_id", "user_id"),
        Index("idx_message_created", "conversation_id", "created_at"),
    )
```

## Conversation Service

```python
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

class ConversationService:
    """Manage conversation lifecycle."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(
        self,
        user_id: str,
        conversation_id: Optional[str] = None
    ) -> Conversation:
        """Get existing or create new conversation."""

        if conversation_id:
            # Load existing
            query = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id  # User isolation!
            )
            result = await self.db.execute(query)
            conversation = result.scalar_one_or_none()

            if conversation:
                return conversation

            # Not found or wrong user - create new

        # Auto-create new conversation
        conversation = Conversation(user_id=user_id)
        self.db.add(conversation)
        await self.db.commit()
        await self.db.refresh(conversation)

        return conversation

    async def load_history(
        self,
        conversation_id: str,
        user_id: str,
        limit: int = 20
    ) -> list[dict]:
        """Fetch message history for agent input."""

        query = (
            select(Message)
            .where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
            .order_by(Message.created_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        messages = result.scalars().all()

        # Reverse to chronological order
        messages = list(reversed(messages))

        # Convert to agent format
        return [
            {
                "role": msg.role,
                "content": msg.content,
                **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
                **({"name": msg.tool_name} if msg.tool_name else {})
            }
            for msg in messages
        ]

    async def save_message(
        self,
        conversation_id: str,
        user_id: str,
        role: str,
        content: str,
        tool_call_id: Optional[str] = None,
        tool_name: Optional[str] = None
    ) -> Message:
        """Save a single message."""

        message = Message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            tool_call_id=tool_call_id,
            tool_name=tool_name
        )

        self.db.add(message)

        # Update conversation timestamp
        await self.db.execute(
            update(Conversation)
            .where(Conversation.id == conversation_id)
            .values(updated_at=datetime.utcnow())
        )

        await self.db.commit()
        await self.db.refresh(message)

        return message

    async def save_exchange(
        self,
        conversation_id: str,
        user_id: str,
        user_message: str,
        assistant_response: str,
        tool_calls: list[dict] = None
    ):
        """Save complete exchange (user + tools + assistant)."""

        # Save user message
        await self.save_message(
            conversation_id, user_id, "user", user_message
        )

        # Save tool call results
        if tool_calls:
            for tool in tool_calls:
                await self.save_message(
                    conversation_id,
                    user_id,
                    "tool",
                    tool["content"],
                    tool_call_id=tool.get("tool_call_id"),
                    tool_name=tool.get("name")
                )

        # Save assistant response
        await self.save_message(
            conversation_id, user_id, "assistant", assistant_response
        )

    async def list_conversations(
        self,
        user_id: str,
        limit: int = 10
    ) -> list[Conversation]:
        """List user's recent conversations."""

        query = (
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.updated_at.desc())
            .limit(limit)
        )

        result = await self.db.execute(query)
        return result.scalars().all()

    async def delete_conversation(
        self,
        conversation_id: str,
        user_id: str
    ) -> bool:
        """Delete conversation and all messages."""

        # Delete messages first
        await self.db.execute(
            delete(Message).where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            )
        )

        # Delete conversation
        result = await self.db.execute(
            delete(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
        )

        await self.db.commit()
        return result.rowcount > 0
```

## Usage in Endpoint

```python
@app.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    db: AsyncSession = Depends(get_db)
):
    service = ConversationService(db)

    # 1. Get or create conversation
    conversation = await service.get_or_create(
        user_id=user_id,
        conversation_id=request.conversation_id
    )

    # 2. Load history (last 20 messages)
    messages = await service.load_history(
        conversation_id=conversation.id,
        user_id=user_id,
        limit=20
    )

    # 3. Add current user message
    messages.append({"role": "user", "content": request.message})

    # 4. Run agent...
    response = await run_agent(messages)

    # 5. Save complete exchange
    await service.save_exchange(
        conversation_id=conversation.id,
        user_id=user_id,
        user_message=request.message,
        assistant_response=response.content,
        tool_calls=response.tool_results
    )

    return {
        "response": response.content,
        "conversation_id": conversation.id
    }
```

## Context Window Management

```python
async def load_history_smart(
    self,
    conversation_id: str,
    user_id: str,
    max_messages: int = 20,
    max_tokens: int = 4000  # Approximate
) -> list[dict]:
    """Load history with token-aware truncation."""

    # Fetch more than needed
    query = (
        select(Message)
        .where(
            Message.conversation_id == conversation_id,
            Message.user_id == user_id
        )
        .order_by(Message.created_at.desc())
        .limit(max_messages * 2)
    )

    result = await self.db.execute(query)
    messages = list(reversed(result.scalars().all()))

    # Estimate tokens and truncate
    selected = []
    token_count = 0

    for msg in reversed(messages):
        # Rough estimate: 1 token ≈ 4 chars
        msg_tokens = len(msg.content) // 4

        if token_count + msg_tokens > max_tokens:
            break

        selected.insert(0, msg)
        token_count += msg_tokens

    # Ensure at least last few messages
    if len(selected) < 5 and len(messages) >= 5:
        selected = messages[-5:]

    return [format_message(msg) for msg in selected]
```

## Server Restart Resilience

```python
# All state in DB - no in-memory caching
# Conversation resumes automatically:

# Request 1 (before restart):
# POST /api/user123/chat
# {"message": "Add buy milk", "conversation_id": "conv-abc"}
# Response: "Added 'buy milk' to your tasks!"

# --- SERVER RESTARTS ---

# Request 2 (after restart):
# POST /api/user123/chat
# {"message": "What's on my list?", "conversation_id": "conv-abc"}
# Response: "You have 1 task: buy milk"
# ✅ Context preserved from DB
```

## Checklist

- [ ] Conversation model with user_id index
- [ ] Message model with role/content/timestamp
- [ ] Composite indexes for fast lookups
- [ ] Get or create conversation logic
- [ ] Load history with limit (20-30 messages)
- [ ] Save user/assistant/tool messages
- [ ] Async queries with SQLModel
- [ ] User isolation on all queries
- [ ] Context window management
- [ ] Conversation survives server restart
