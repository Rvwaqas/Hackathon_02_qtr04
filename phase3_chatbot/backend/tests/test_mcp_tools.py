"""
Unit tests for MCP Tools (TodoToolsHandler).

Tests cover:
- Task creation with valid/invalid inputs
- Task listing with filtering
- Task completion
- Task updates
- Task deletion
- User data isolation
- Error handling
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.mcp.tools import TodoToolsHandler
from src.models.task import Task
from src.schemas.task import TaskCreate


# Test database setup
TEST_DATABASE_URL = "sqlite+asyncio:///:memory:"


@pytest.fixture
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

    from sqlalchemy.ext.asyncio import AsyncSession
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest.fixture
async def tools_handler(async_session):
    """Create TodoToolsHandler instance."""
    return TodoToolsHandler(async_session, user_id="test-user-1")


# ============ Add Task Tests ============

@pytest.mark.asyncio
async def test_add_task_minimal(tools_handler):
    """Test adding task with only required field."""
    result = await tools_handler.add_task(
        title="Buy groceries"
    )

    assert result["success"] is True
    assert result["task_id"]
    assert "added" in result["message"].lower()
    assert "✅" in result["message"]


@pytest.mark.asyncio
async def test_add_task_full(tools_handler):
    """Test adding task with all fields."""
    result = await tools_handler.add_task(
        title="Buy groceries",
        description="Milk, eggs, bread",
        priority="high",
        due_date="2024-12-31"
    )

    assert result["success"] is True
    assert result["task_id"]
    assert "added" in result["message"].lower()


@pytest.mark.asyncio
async def test_add_task_empty_title(tools_handler):
    """Test error when title is empty."""
    result = await tools_handler.add_task(title="")

    assert result["success"] is False
    assert result["error"] == "invalid_input"
    assert "required" in result["message"].lower()


@pytest.mark.asyncio
async def test_add_task_whitespace_title(tools_handler):
    """Test error when title is only whitespace."""
    result = await tools_handler.add_task(title="   ")

    assert result["success"] is False
    assert result["error"] == "invalid_input"


@pytest.mark.asyncio
async def test_add_task_with_tags(tools_handler):
    """Test adding task with tags."""
    result = await tools_handler.add_task(
        title="Shopping",
        tags=["errands", "shopping"]
    )

    assert result["success"] is True
    assert result["task_id"]


# ============ List Tasks Tests ============

@pytest.mark.asyncio
async def test_list_tasks_empty(tools_handler):
    """Test listing when no tasks exist."""
    result = await tools_handler.list_tasks()

    assert result["success"] is True
    assert result["count"] == 0
    assert result["tasks"] == []


@pytest.mark.asyncio
async def test_list_tasks_after_add(tools_handler):
    """Test listing tasks after adding some."""
    # Add tasks
    await tools_handler.add_task(title="Task 1")
    await tools_handler.add_task(title="Task 2")

    result = await tools_handler.list_tasks()

    assert result["success"] is True
    assert result["count"] == 2
    assert len(result["tasks"]) == 2
    assert result["tasks"][0]["title"] in ["Task 1", "Task 2"]


@pytest.mark.asyncio
async def test_list_tasks_filter_status(tools_handler):
    """Test listing tasks with status filter."""
    # Add and complete a task
    add_result = await tools_handler.add_task(title="Task 1")
    task_id = add_result["task_id"]

    await tools_handler.complete_task(task_id)

    # List pending only
    result = await tools_handler.list_tasks(status="pending")
    assert result["count"] == 0

    # List completed only
    result = await tools_handler.list_tasks(status="completed")
    assert result["count"] == 1


@pytest.mark.asyncio
async def test_list_tasks_filter_priority(tools_handler):
    """Test listing tasks with priority filter."""
    await tools_handler.add_task(title="Task 1", priority="high")
    await tools_handler.add_task(title="Task 2", priority="low")

    result = await tools_handler.list_tasks(priority="high")
    assert result["count"] == 1
    assert result["tasks"][0]["priority"] == "high"


@pytest.mark.asyncio
async def test_list_tasks_filter_all(tools_handler):
    """Test listing all tasks regardless of status/priority."""
    await tools_handler.add_task(title="Task 1", priority="high")
    await tools_handler.add_task(title="Task 2", priority="low")

    result = await tools_handler.list_tasks(status="all", priority="all")
    assert result["count"] == 2


# ============ Complete Task Tests ============

@pytest.mark.asyncio
async def test_complete_task(tools_handler):
    """Test completing a task."""
    # Add task
    add_result = await tools_handler.add_task(title="Task to complete")
    task_id = add_result["task_id"]

    # Complete it
    result = await tools_handler.complete_task(task_id)

    assert result["success"] is True
    assert "complete" in result["message"].lower()
    assert "🎉" in result["message"]


@pytest.mark.asyncio
async def test_complete_task_not_found(tools_handler):
    """Test error when task doesn't exist."""
    result = await tools_handler.complete_task("99999")

    assert result["success"] is False
    assert result["error"] == "not_found"


@pytest.mark.asyncio
async def test_complete_task_already_completed(tools_handler):
    """Test error when trying to complete already completed task."""
    # Add and complete
    add_result = await tools_handler.add_task(title="Task")
    task_id = add_result["task_id"]
    await tools_handler.complete_task(task_id)

    # Try to complete again
    result = await tools_handler.complete_task(task_id)

    assert result["success"] is False
    assert result["error"] == "already_completed"


@pytest.mark.asyncio
async def test_complete_task_invalid_id(tools_handler):
    """Test error with invalid task ID format."""
    result = await tools_handler.complete_task("not-a-number")

    assert result["success"] is False
    assert result["error"] == "invalid_id"


# ============ Update Task Tests ============

@pytest.mark.asyncio
async def test_update_task_title(tools_handler):
    """Test updating task title."""
    add_result = await tools_handler.add_task(title="Original title")
    task_id = add_result["task_id"]

    result = await tools_handler.update_task(task_id, title="New title")

    assert result["success"] is True
    assert "updated" in result["message"].lower()
    assert "✏️" in result["message"]


@pytest.mark.asyncio
async def test_update_task_priority(tools_handler):
    """Test updating task priority."""
    add_result = await tools_handler.add_task(title="Task", priority="low")
    task_id = add_result["task_id"]

    result = await tools_handler.update_task(task_id, priority="high")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_task_status(tools_handler):
    """Test updating task status to completed."""
    add_result = await tools_handler.add_task(title="Task")
    task_id = add_result["task_id"]

    result = await tools_handler.update_task(task_id, status="completed")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_task_no_changes(tools_handler):
    """Test error when no fields provided."""
    add_result = await tools_handler.add_task(title="Task")
    task_id = add_result["task_id"]

    result = await tools_handler.update_task(task_id)

    assert result["success"] is False
    assert result["error"] == "no_updates"


@pytest.mark.asyncio
async def test_update_task_not_found(tools_handler):
    """Test error when task doesn't exist."""
    result = await tools_handler.update_task("99999", title="New title")

    assert result["success"] is False
    assert result["error"] == "not_found"


# ============ Delete Task Tests ============

@pytest.mark.asyncio
async def test_delete_task(tools_handler):
    """Test deleting a task."""
    add_result = await tools_handler.add_task(title="Task to delete")
    task_id = add_result["task_id"]

    result = await tools_handler.delete_task(task_id)

    assert result["success"] is True
    assert "deleted" in result["message"].lower()
    assert "✂️" in result["message"]

    # Verify it's deleted
    list_result = await tools_handler.list_tasks()
    assert list_result["count"] == 0


@pytest.mark.asyncio
async def test_delete_task_not_found(tools_handler):
    """Test error when task doesn't exist."""
    result = await tools_handler.delete_task("99999")

    assert result["success"] is False
    assert result["error"] == "not_found"


@pytest.mark.asyncio
async def test_delete_task_invalid_id(tools_handler):
    """Test error with invalid task ID."""
    result = await tools_handler.delete_task("invalid")

    assert result["success"] is False
    assert result["error"] == "invalid_id"


# ============ User Isolation Tests ============

@pytest.mark.asyncio
async def test_user_isolation(async_session):
    """Test that different users can't access each other's tasks."""
    user1_handler = TodoToolsHandler(async_session, user_id="user-1")
    user2_handler = TodoToolsHandler(async_session, user_id="user-2")

    # User 1 adds task
    result1 = await user1_handler.add_task(title="User 1 secret task")
    assert result1["success"] is True

    # User 1 lists tasks
    list1 = await user1_handler.list_tasks()
    assert list1["count"] == 1

    # User 2 lists tasks - should see none
    list2 = await user2_handler.list_tasks()
    assert list2["count"] == 0


# ============ Integration Tests ============

@pytest.mark.asyncio
async def test_full_task_lifecycle(tools_handler):
    """Test complete task lifecycle: add, update, complete, delete."""
    # 1. Add task
    add_result = await tools_handler.add_task(
        title="Complete me",
        priority="low"
    )
    task_id = add_result["task_id"]
    assert add_result["success"] is True

    # 2. Update priority
    update_result = await tools_handler.update_task(task_id, priority="high")
    assert update_result["success"] is True

    # 3. Complete task
    complete_result = await tools_handler.complete_task(task_id)
    assert complete_result["success"] is True

    # 4. List to verify completion
    list_result = await tools_handler.list_tasks(status="completed")
    assert list_result["count"] == 1

    # 5. Delete task
    delete_result = await tools_handler.delete_task(task_id)
    assert delete_result["success"] is True

    # 6. Verify deletion
    final_list = await tools_handler.list_tasks()
    assert final_list["count"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
