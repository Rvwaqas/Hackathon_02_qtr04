"""
Unit tests for Phase V Part A - Event Publishing via Dapr Pub/Sub.

Tests cover:
- Event published on task creation (T549)
- Event published on task update (T550)
- Event published on task completion (T551)
- Event published on task deletion (T552)
- CloudEvents schema validation (T553)
- Graceful degradation when Dapr unavailable (T554)
"""

import pytest
import pytest_asyncio
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

import httpx

from src.services.event_publisher import EventPublisher, event_publisher
from src.services.task import TaskService
from src.schemas import TaskCreate, TaskUpdate
from src.models.task import Task


# Test database setup
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_session():
    """Create async test database session."""
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


@pytest.fixture
def mock_httpx_success():
    """Mock httpx client with successful response."""
    with patch("src.services.event_publisher.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 204

        mock_instance = AsyncMock()
        mock_instance.post = AsyncMock(return_value=mock_response)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)

        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_httpx_failure():
    """Mock httpx client with connection error."""
    with patch("src.services.event_publisher.httpx.AsyncClient") as mock_client:
        mock_instance = AsyncMock()
        mock_instance.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)

        mock_client.return_value = mock_instance
        yield mock_instance


# ============ T549: Event on Task Creation ============

@pytest.mark.asyncio
async def test_event_published_on_create(async_session, mock_httpx_success):
    """T549: Verify event is published when task is created."""
    task_data = TaskCreate(
        title="Test task",
        description="Test description",
        priority="high",
        tags=["test"]
    )

    task = await TaskService.create_task(async_session, user_id=1, data=task_data)

    # Verify HTTP POST was called
    mock_httpx_success.post.assert_called()

    # Verify call details
    call_args = mock_httpx_success.post.call_args
    url = call_args[0][0] if call_args[0] else call_args.kwargs.get("url")
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert "task-events" in url
    assert json_data["type"] == "com.todo.task.created"
    assert json_data["data"]["task_id"] == task.id
    assert json_data["data"]["title"] == "Test task"


@pytest.mark.asyncio
async def test_create_event_contains_task_data(async_session, mock_httpx_success):
    """T549: Verify created event contains full task data snapshot."""
    task_data = TaskCreate(
        title="Full data test",
        description="With description",
        priority="medium",
        tags=["tag1", "tag2"]
    )

    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")
    event_data = json_data["data"]

    assert event_data["title"] == "Full data test"
    assert event_data["description"] == "With description"
    assert event_data["priority"] == "medium"
    assert event_data["tags"] == ["tag1", "tag2"]
    assert event_data["completed"] is False


# ============ T550: Event on Task Update ============

@pytest.mark.asyncio
async def test_event_published_on_update(async_session, mock_httpx_success):
    """T550: Verify event is published when task is updated."""
    # Create task first
    task_data = TaskCreate(title="Original title")
    task = await TaskService.create_task(async_session, user_id=1, data=task_data)

    # Reset mock to track update call
    mock_httpx_success.post.reset_mock()

    # Update task
    update_data = TaskUpdate(title="Updated title", priority="high")
    await TaskService.update_task(async_session, task.id, user_id=1, data=update_data)

    # Verify update event was published
    mock_httpx_success.post.assert_called()
    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert json_data["type"] == "com.todo.task.updated"
    assert json_data["data"]["title"] == "Updated title"
    assert json_data["data"]["priority"] == "high"


# ============ T551: Event on Task Completion ============

@pytest.mark.asyncio
async def test_event_published_on_completion(async_session, mock_httpx_success):
    """T551: Verify event is published when task is completed."""
    # Create task
    task_data = TaskCreate(title="Task to complete")
    task = await TaskService.create_task(async_session, user_id=1, data=task_data)

    # Reset mock
    mock_httpx_success.post.reset_mock()

    # Complete task
    await TaskService.toggle_complete(async_session, task.id, user_id=1)

    # Verify completion event
    mock_httpx_success.post.assert_called()
    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert json_data["type"] == "com.todo.task.completed"
    assert json_data["data"]["task_id"] == task.id


# ============ T552: Event on Task Deletion ============

@pytest.mark.asyncio
async def test_event_published_on_delete(async_session, mock_httpx_success):
    """T552: Verify event is published when task is deleted."""
    # Create task
    task_data = TaskCreate(title="Task to delete")
    task = await TaskService.create_task(async_session, user_id=1, data=task_data)
    task_id = task.id

    # Reset mock
    mock_httpx_success.post.reset_mock()

    # Delete task
    await TaskService.delete_task(async_session, task_id, user_id=1)

    # Verify deletion event
    mock_httpx_success.post.assert_called()
    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert json_data["type"] == "com.todo.task.deleted"
    assert json_data["data"]["task_id"] == task_id


# ============ T553: CloudEvents Schema Validation ============

@pytest.mark.asyncio
async def test_cloudevents_schema_specversion(async_session, mock_httpx_success):
    """T553: Verify CloudEvents specversion is 1.0."""
    task_data = TaskCreate(title="Schema test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert json_data["specversion"] == "1.0"


@pytest.mark.asyncio
async def test_cloudevents_schema_required_fields(async_session, mock_httpx_success):
    """T553: Verify CloudEvents contains all required fields."""
    task_data = TaskCreate(title="Schema test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    # Required CloudEvents fields
    assert "specversion" in json_data
    assert "type" in json_data
    assert "source" in json_data
    assert "id" in json_data
    assert "time" in json_data
    assert "datacontenttype" in json_data
    assert "data" in json_data


@pytest.mark.asyncio
async def test_cloudevents_schema_type_format(async_session, mock_httpx_success):
    """T553: Verify event type follows reverse-DNS format."""
    task_data = TaskCreate(title="Type format test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    # Should follow com.todo.* pattern
    assert json_data["type"].startswith("com.todo.")


@pytest.mark.asyncio
async def test_cloudevents_schema_source(async_session, mock_httpx_success):
    """T553: Verify source field is valid URI path."""
    task_data = TaskCreate(title="Source test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert json_data["source"].startswith("/")


@pytest.mark.asyncio
async def test_cloudevents_schema_id_unique(async_session, mock_httpx_success):
    """T553: Verify each event has unique ID (UUID format)."""
    task_data = TaskCreate(title="ID test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    # UUID format check (basic)
    event_id = json_data["id"]
    assert len(event_id) == 36  # UUID length with dashes
    assert event_id.count("-") == 4  # UUID has 4 dashes


@pytest.mark.asyncio
async def test_cloudevents_schema_time_iso8601(async_session, mock_httpx_success):
    """T553: Verify time field is ISO 8601 format."""
    task_data = TaskCreate(title="Time test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    # Should end with Z (UTC)
    assert json_data["time"].endswith("Z")
    # Should be parseable
    time_str = json_data["time"].rstrip("Z")
    datetime.fromisoformat(time_str)  # Should not raise


@pytest.mark.asyncio
async def test_cloudevents_schema_datacontenttype(async_session, mock_httpx_success):
    """T553: Verify datacontenttype is application/json."""
    task_data = TaskCreate(title="Content type test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    call_args = mock_httpx_success.post.call_args
    json_data = call_args.kwargs.get("json") or call_args[1].get("json")

    assert json_data["datacontenttype"] == "application/json"


# ============ T554: Graceful Degradation ============

@pytest.mark.asyncio
async def test_graceful_degradation_task_created(async_session, mock_httpx_failure):
    """T554: Task creation succeeds even when Dapr is unavailable."""
    task_data = TaskCreate(title="Offline test")

    # This should NOT raise an exception
    task = await TaskService.create_task(async_session, user_id=1, data=task_data)

    # Task should be created successfully
    assert task is not None
    assert task.id is not None
    assert task.title == "Offline test"


@pytest.mark.asyncio
async def test_graceful_degradation_task_updated(async_session, mock_httpx_failure):
    """T554: Task update succeeds even when Dapr is unavailable."""
    # Create task with working mock first
    with patch("src.services.event_publisher.httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_instance = AsyncMock()
        mock_instance.post = AsyncMock(return_value=mock_response)
        mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
        mock_instance.__aexit__ = AsyncMock(return_value=None)
        mock_client.return_value = mock_instance

        task_data = TaskCreate(title="Original")
        task = await TaskService.create_task(async_session, user_id=1, data=task_data)

    # Update with failing mock - should still succeed
    update_data = TaskUpdate(title="Updated")
    updated_task = await TaskService.update_task(async_session, task.id, user_id=1, data=update_data)

    assert updated_task is not None
    assert updated_task.title == "Updated"


@pytest.mark.asyncio
async def test_graceful_degradation_logs_error(async_session, mock_httpx_failure, caplog):
    """T554: Error is logged when event publishing fails."""
    import logging
    caplog.set_level(logging.ERROR)

    task_data = TaskCreate(title="Log test")
    await TaskService.create_task(async_session, user_id=1, data=task_data)

    # Check that error was logged
    assert any("unavailable" in record.message.lower() or "error" in record.message.lower()
               for record in caplog.records)


# ============ EventPublisher Unit Tests ============

@pytest.mark.asyncio
async def test_event_publisher_publish_success(mock_httpx_success):
    """Test EventPublisher.publish returns True on success."""
    publisher = EventPublisher()

    result = await publisher.publish(
        topic="test-topic",
        event_type="com.test.event",
        source="/test",
        data={"key": "value"}
    )

    assert result is True


@pytest.mark.asyncio
async def test_event_publisher_publish_failure(mock_httpx_failure):
    """Test EventPublisher.publish returns False on failure."""
    publisher = EventPublisher()

    result = await publisher.publish(
        topic="test-topic",
        event_type="com.test.event",
        source="/test",
        data={"key": "value"}
    )

    assert result is False


@pytest.mark.asyncio
async def test_event_publisher_creates_valid_cloudevent():
    """Test _create_cloud_event produces valid structure."""
    publisher = EventPublisher()

    event = publisher._create_cloud_event(
        event_type="com.test.type",
        source="/test/source",
        data={"test": "data"}
    )

    assert event["specversion"] == "1.0"
    assert event["type"] == "com.test.type"
    assert event["source"] == "/test/source"
    assert event["data"] == {"test": "data"}
    assert "id" in event
    assert "time" in event


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
