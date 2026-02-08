"""
Integration tests for Chat API endpoints.

Tests cover:
- Chat message sending and response
- Conversation creation and retrieval
- Message history persistence
- User data isolation
- Error handling and edge cases
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session
from unittest.mock import patch, AsyncMock

from src.main import app
from src.database import get_session
from src.middleware import get_current_user_id
from src.config import settings


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Test data
TEST_USER_ID = 1


@pytest_asyncio.fixture
async def async_db():
    """Create test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


def override_get_current_user_id():
    """Override to return test user ID."""
    return TEST_USER_ID


@pytest_asyncio.fixture
async def client(async_db):
    """Create test client with test database and mocked auth."""

    async def override_get_session():
        yield async_db

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    # Mock TodoAgent to avoid real API calls
    with patch('src.api.chat.TodoAgent') as mock_agent_class:
        mock_agent = AsyncMock()
        mock_agent.execute = AsyncMock(return_value="Task added successfully! [COMPLETED]")
        mock_agent_class.return_value = mock_agent

        with TestClient(app) as client:
            yield client

    app.dependency_overrides.clear()


# Test data
VALID_JWT_TOKEN = "test-token"  # Not used since auth is mocked


# ============ Chat Endpoint Tests ============

def test_send_message_creates_conversation(client):
    """Test that sending a message creates a new conversation."""
    response = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={"message": "Add a task to buy groceries"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["message"]  # Should have response from agent
    assert data["conversation_id"]  # Should create new conversation
    assert data["role"] == "assistant"


def test_send_message_with_existing_conversation(client):
    """Test sending message to existing conversation."""
    # Create first message
    response1 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={"message": "Add groceries task"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # Send message to same conversation
    response2 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={
            "message": "Show my tasks",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response2.status_code == 200
    data = response2.json()
    assert data["conversation_id"] == conversation_id


def test_send_message_forbidden_cross_user(client):
    """Test that users cannot access other users' conversations."""
    response = client.post(
        f"/api/999/chat",  # Different user ID
        json={"message": "Test message"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 403
    assert "Cannot access" in response.json()["detail"]


def test_send_message_invalid_conversation_id(client):
    """Test error handling for invalid conversation ID format."""
    response = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={
            "message": "Test",
            "conversation_id": "not-a-valid-uuid"
        },
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


def test_send_message_missing_message_field(client):
    """Test error when message field is missing."""
    response = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 422  # Validation error


# ============ Conversation List Tests ============

def test_get_conversations_empty(client):
    """Test getting conversations list when user has no conversations."""
    response = client.get(
        f"/api/{TEST_USER_ID}/conversations",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_conversations_after_messages(client):
    """Test getting conversations list after creating some conversations."""
    # Send multiple messages to create conversations
    for i in range(3):
        client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={"message": f"Task {i}"},
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
        )

    response = client.get(
        f"/api/{TEST_USER_ID}/conversations",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3  # Should have 3 conversations


def test_get_conversations_forbidden_cross_user(client):
    """Test that users cannot list other users' conversations."""
    response = client.get(
        f"/api/999/conversations",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 403


# ============ Conversation Detail Tests ============

def test_get_conversation_detail(client):
    """Test retrieving full conversation with message history."""
    # Send a message
    response1 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={"message": "Add groceries"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    conversation_id = response1.json()["conversation_id"]

    # Get conversation detail
    response2 = client.get(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response2.status_code == 200
    data = response2.json()
    assert data["id"] == conversation_id
    assert len(data["messages"]) >= 2  # User message + assistant response


def test_get_conversation_detail_not_found(client):
    """Test error when conversation doesn't exist."""
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.get(
        f"/api/{TEST_USER_ID}/conversations/{fake_uuid}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_get_conversation_detail_invalid_uuid(client):
    """Test error with invalid UUID format."""
    response = client.get(
        f"/api/{TEST_USER_ID}/conversations/not-a-uuid",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 400
    assert "Invalid" in response.json()["detail"]


def test_get_conversation_detail_forbidden_cross_user(client):
    """Test that users cannot view other users' conversations."""
    # Create conversation for user 1
    response1 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={"message": "My secret task"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    conversation_id = response1.json()["conversation_id"]

    # Try to access as different user
    response2 = client.get(
        f"/api/999/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response2.status_code == 403


# ============ Delete Conversation Tests ============

def test_delete_conversation(client):
    """Test deleting a conversation."""
    # Create conversation
    response1 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={"message": "Delete me"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    conversation_id = response1.json()["conversation_id"]

    # Delete it
    response2 = client.delete(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response2.status_code == 204

    # Verify it's deleted
    response3 = client.get(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response3.status_code == 404


def test_delete_conversation_not_found(client):
    """Test error when deleting non-existent conversation."""
    fake_uuid = "123e4567-e89b-12d3-a456-426614174000"
    response = client.delete(
        f"/api/{TEST_USER_ID}/conversations/{fake_uuid}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 404


def test_delete_conversation_forbidden_cross_user(client):
    """Test that users cannot delete other users' conversations."""
    response = client.delete(
        f"/api/999/conversations/123e4567-e89b-12d3-a456-426614174000",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 403


# ============ Integration Tests ============

def test_full_conversation_flow(client):
    """Test complete conversation flow: create, send multiple messages, retrieve, delete."""
    # 1. Send first message (creates conversation)
    response1 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={"message": "Add a task"},
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response1.status_code == 200
    conversation_id = response1.json()["conversation_id"]

    # 2. Send second message to same conversation
    response2 = client.post(
        f"/api/{TEST_USER_ID}/chat",
        json={
            "message": "List my tasks",
            "conversation_id": conversation_id
        },
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response2.status_code == 200

    # 3. Get conversation detail
    response3 = client.get(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response3.status_code == 200
    data = response3.json()
    assert len(data["messages"]) >= 4  # 2 user + 2 assistant responses

    # 4. List conversations
    response4 = client.get(
        f"/api/{TEST_USER_ID}/conversations",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response4.status_code == 200
    assert len(response4.json()) >= 1

    # 5. Delete conversation
    response5 = client.delete(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response5.status_code == 204

    # 6. Verify deleted
    response6 = client.get(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )
    assert response6.status_code == 404


def test_message_history_context(client):
    """Test that message history is properly maintained for context."""
    conversation_id = None

    # Send 3 messages in sequence
    messages = [
        "Add task 1",
        "Add task 2",
        "Show all tasks"
    ]

    for msg in messages:
        response = client.post(
            f"/api/{TEST_USER_ID}/chat",
            json={
                "message": msg,
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
        )
        assert response.status_code == 200
        if not conversation_id:
            conversation_id = response.json()["conversation_id"]

    # Get full history
    response = client.get(
        f"/api/{TEST_USER_ID}/conversations/{conversation_id}",
        headers={"Authorization": f"Bearer {VALID_JWT_TOKEN}"},
    )

    assert response.status_code == 200
    messages_data = response.json()["messages"]
    assert len(messages_data) == 6  # 3 user + 3 assistant


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
