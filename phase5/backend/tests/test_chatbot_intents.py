"""
Unit tests for Phase V Part A - Chatbot Intent Recognition.

Tests cover:
- Priority intent recognition (T556)
- Tag intent recognition (T557)
- Search intent recognition (T558)
- Filter intent recognition (T559)
- Sort intent recognition (T560)
- Recurrence intent recognition (T561)
- Backward compatibility with Phase III (T562)

Note: These tests verify the system prompt patterns and tool definitions
are correctly configured to guide the LLM in recognizing user intents.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.agents.config import SYSTEM_PROMPT, TOOL_DEFINITIONS
from src.mcp.tools import TodoToolsHandler


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


@pytest_asyncio.fixture
async def tools_handler(async_session):
    """Create TodoToolsHandler instance."""
    return TodoToolsHandler(async_session, user_id="1")


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


# ============ System Prompt Pattern Tests ============

class TestSystemPromptPatterns:
    """Verify system prompt contains required intent recognition patterns."""

    # T556: Priority Recognition
    def test_priority_high_patterns_in_prompt(self):
        """T556: System prompt contains high priority recognition patterns."""
        assert "high priority" in SYSTEM_PROMPT.lower()
        assert "urgent" in SYSTEM_PROMPT.lower()
        assert "important" in SYSTEM_PROMPT.lower()

    def test_priority_medium_patterns_in_prompt(self):
        """T556: System prompt contains medium priority recognition patterns."""
        assert "medium priority" in SYSTEM_PROMPT.lower() or "medium" in SYSTEM_PROMPT.lower()

    def test_priority_low_patterns_in_prompt(self):
        """T556: System prompt contains low priority recognition patterns."""
        assert "low priority" in SYSTEM_PROMPT.lower()

    # T557: Tag Recognition
    def test_tag_patterns_in_prompt(self):
        """T557: System prompt contains tag recognition patterns."""
        assert "tagged" in SYSTEM_PROMPT.lower()
        assert "tag" in SYSTEM_PROMPT.lower()

    # T558: Search Recognition
    def test_search_patterns_in_prompt(self):
        """T558: System prompt contains search recognition patterns."""
        assert "find" in SYSTEM_PROMPT.lower() or "search" in SYSTEM_PROMPT.lower()

    # T559: Filter Recognition
    def test_filter_patterns_in_prompt(self):
        """T559: System prompt contains filter recognition patterns."""
        assert "filter" in SYSTEM_PROMPT.lower() or "show only" in SYSTEM_PROMPT.lower()

    # T560: Sort Recognition
    def test_sort_patterns_in_prompt(self):
        """T560: System prompt contains sort recognition patterns."""
        assert "sort" in SYSTEM_PROMPT.lower()
        assert "order" in SYSTEM_PROMPT.lower() or "by" in SYSTEM_PROMPT.lower()

    # T561: Recurrence Recognition
    def test_recurrence_patterns_in_prompt(self):
        """T561: System prompt contains recurrence recognition patterns."""
        assert "repeat" in SYSTEM_PROMPT.lower() or "recurring" in SYSTEM_PROMPT.lower()
        assert "daily" in SYSTEM_PROMPT.lower()
        assert "weekly" in SYSTEM_PROMPT.lower()
        assert "monthly" in SYSTEM_PROMPT.lower()

    def test_due_date_patterns_in_prompt(self):
        """System prompt contains due date recognition patterns."""
        assert "due" in SYSTEM_PROMPT.lower()
        assert "tomorrow" in SYSTEM_PROMPT.lower() or "friday" in SYSTEM_PROMPT.lower()

    def test_reminder_patterns_in_prompt(self):
        """System prompt contains reminder recognition patterns."""
        assert "remind" in SYSTEM_PROMPT.lower()
        assert "before" in SYSTEM_PROMPT.lower()


# ============ Tool Definition Tests ============

class TestToolDefinitions:
    """Verify tool definitions contain required parameters."""

    def get_tool_def(self, name: str):
        """Get tool definition by name."""
        for tool in TOOL_DEFINITIONS:
            if tool["name"] == name:
                return tool
        return None

    # T556-T561: add_task tool parameters
    def test_add_task_has_priority(self):
        """add_task tool has priority parameter."""
        tool = self.get_tool_def("add_task")
        assert tool is not None
        assert "priority" in tool["parameters"]["properties"]

    def test_add_task_has_tags(self):
        """add_task tool has tags parameter."""
        tool = self.get_tool_def("add_task")
        assert "tags" in tool["parameters"]["properties"]
        assert tool["parameters"]["properties"]["tags"]["type"] == "array"

    def test_add_task_has_recurrence(self):
        """add_task tool has recurrence parameter."""
        tool = self.get_tool_def("add_task")
        assert "recurrence" in tool["parameters"]["properties"]
        assert tool["parameters"]["properties"]["recurrence"]["type"] == "object"

    def test_add_task_has_reminder(self):
        """add_task tool has reminder_offset_minutes parameter."""
        tool = self.get_tool_def("add_task")
        assert "reminder_offset_minutes" in tool["parameters"]["properties"]

    def test_add_task_has_due_date(self):
        """add_task tool has due_date parameter."""
        tool = self.get_tool_def("add_task")
        assert "due_date" in tool["parameters"]["properties"]

    # list_tasks tool parameters
    def test_list_tasks_has_search(self):
        """list_tasks tool has search parameter."""
        tool = self.get_tool_def("list_tasks")
        assert tool is not None
        assert "search" in tool["parameters"]["properties"]

    def test_list_tasks_has_tag(self):
        """list_tasks tool has tag filter parameter."""
        tool = self.get_tool_def("list_tasks")
        assert "tag" in tool["parameters"]["properties"]

    def test_list_tasks_has_sort(self):
        """list_tasks tool has sort parameter."""
        tool = self.get_tool_def("list_tasks")
        assert "sort" in tool["parameters"]["properties"]
        # Check sort options
        sort_enum = tool["parameters"]["properties"]["sort"].get("enum", [])
        assert "due_date" in sort_enum
        assert "priority" in sort_enum
        assert "created_at" in sort_enum

    def test_list_tasks_has_order(self):
        """list_tasks tool has order parameter."""
        tool = self.get_tool_def("list_tasks")
        assert "order" in tool["parameters"]["properties"]
        order_enum = tool["parameters"]["properties"]["order"].get("enum", [])
        assert "asc" in order_enum
        assert "desc" in order_enum

    # update_task tool parameters
    def test_update_task_has_tags(self):
        """update_task tool has tags parameter."""
        tool = self.get_tool_def("update_task")
        assert tool is not None
        assert "tags" in tool["parameters"]["properties"]

    def test_update_task_has_recurrence(self):
        """update_task tool has recurrence parameter."""
        tool = self.get_tool_def("update_task")
        assert "recurrence" in tool["parameters"]["properties"]

    def test_update_task_has_reminder(self):
        """update_task tool has reminder_offset_minutes parameter."""
        tool = self.get_tool_def("update_task")
        assert "reminder_offset_minutes" in tool["parameters"]["properties"]


# ============ T562: Backward Compatibility Tests ============

@pytest.mark.asyncio
async def test_basic_add_task_still_works(tools_handler, mock_httpx_success):
    """T562: Basic 'add task buy milk' command still works."""
    result = await tools_handler.add_task(title="buy milk")

    assert result["success"] is True
    assert "buy milk" in result["message"].lower()


@pytest.mark.asyncio
async def test_basic_list_tasks_still_works(tools_handler, mock_httpx_success):
    """T562: Basic 'show tasks' command still works."""
    # Add a task first
    await tools_handler.add_task(title="test task")

    result = await tools_handler.list_tasks()

    assert result["success"] is True
    assert result["count"] >= 1


@pytest.mark.asyncio
async def test_basic_complete_task_still_works(tools_handler, mock_httpx_success):
    """T562: Basic 'complete task 1' command still works."""
    # Add and get task ID
    add_result = await tools_handler.add_task(title="task to complete")
    task_id = add_result["task_id"]

    result = await tools_handler.complete_task(task_id)

    assert result["success"] is True
    assert "complete" in result["message"].lower() or "done" in result["message"].lower()


@pytest.mark.asyncio
async def test_basic_delete_task_still_works(tools_handler, mock_httpx_success):
    """T562: Basic 'delete task 1' command still works."""
    # Add and get task ID
    add_result = await tools_handler.add_task(title="task to delete")
    task_id = add_result["task_id"]

    result = await tools_handler.delete_task(task_id)

    assert result["success"] is True
    assert "deleted" in result["message"].lower() or "removed" in result["message"].lower()


@pytest.mark.asyncio
async def test_add_with_description_still_works(tools_handler, mock_httpx_success):
    """T562: Adding task with description still works."""
    result = await tools_handler.add_task(
        title="task with desc",
        description="This is a description"
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_title_still_works(tools_handler, mock_httpx_success):
    """T562: Updating task title still works."""
    add_result = await tools_handler.add_task(title="original")
    task_id = add_result["task_id"]

    result = await tools_handler.update_task(task_id, title="updated")

    assert result["success"] is True


@pytest.mark.asyncio
async def test_filter_by_status_still_works(tools_handler, mock_httpx_success):
    """T562: Filtering by status still works."""
    await tools_handler.add_task(title="pending task")

    result = await tools_handler.list_tasks(status="pending")

    assert result["success"] is True
    assert result["count"] >= 1


@pytest.mark.asyncio
async def test_filter_by_priority_still_works(tools_handler, mock_httpx_success):
    """T562: Filtering by priority still works."""
    await tools_handler.add_task(title="high priority task", priority="high")

    result = await tools_handler.list_tasks(priority="high")

    assert result["success"] is True
    assert result["count"] >= 1


# ============ New Feature Integration Tests ============

@pytest.mark.asyncio
async def test_add_with_all_new_features(tools_handler, mock_httpx_success):
    """Integration test: Add task with all Phase V features."""
    result = await tools_handler.add_task(
        title="Complete feature task",
        description="Test all features",
        priority="high",
        tags=["work", "important"],
        due_date="2026-02-07T17:00:00Z",
        recurrence={"type": "weekly", "interval": 1},
        reminder_offset_minutes=60
    )

    assert result["success"] is True
    # Message should mention some of the features
    message = result["message"].lower()
    assert "high" in message or "priority" in message
    assert "tagged" in message or "work" in message or "tag" in message


@pytest.mark.asyncio
async def test_list_with_all_new_filters(tools_handler, mock_httpx_success):
    """Integration test: List tasks with all new filter/sort options."""
    # Add some tasks
    await tools_handler.add_task(
        title="meeting notes",
        priority="high",
        tags=["work"]
    )

    result = await tools_handler.list_tasks(
        status="pending",
        priority="high",
        tag="work",
        search="meeting",
        sort="created_at",
        order="desc"
    )

    assert result["success"] is True


@pytest.mark.asyncio
async def test_update_with_new_features(tools_handler, mock_httpx_success):
    """Integration test: Update task with new Phase V features."""
    add_result = await tools_handler.add_task(title="update me")
    task_id = add_result["task_id"]

    result = await tools_handler.update_task(
        task_id=task_id,
        priority="high",
        tags=["urgent", "work"],
        recurrence={"type": "daily", "interval": 1},
        reminder_offset_minutes=30
    )

    assert result["success"] is True
    # Message should describe the changes
    assert "updated" in result["message"].lower()


# ============ Example Interactions from System Prompt ============

class TestExampleInteractions:
    """Verify example interactions from system prompt work correctly."""

    @pytest.mark.asyncio
    async def test_example_high_priority_meeting(self, tools_handler, mock_httpx_success):
        """Example: 'add high priority task meeting due Friday tagged work'"""
        result = await tools_handler.add_task(
            title="meeting",
            priority="high",
            due_date="2026-02-07",  # Simulated "next Friday"
            tags=["work"]
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_example_pending_work_sorted(self, tools_handler, mock_httpx_success):
        """Example: 'show pending tasks tagged work sorted by due date'"""
        # Add task first
        await tools_handler.add_task(
            title="work task",
            tags=["work"],
            due_date="2026-02-10"
        )

        result = await tools_handler.list_tasks(
            status="pending",
            tag="work",
            sort="due_date"
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_example_weekly_standup_with_reminder(self, tools_handler, mock_httpx_success):
        """Example: 'add task weekly standup repeat weekly remind me 30 minutes before'"""
        result = await tools_handler.add_task(
            title="weekly standup",
            recurrence={"type": "weekly", "interval": 1},
            reminder_offset_minutes=30
        )

        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_example_search_groceries(self, tools_handler, mock_httpx_success):
        """Example: 'find tasks about groceries'"""
        # Add task with "groceries" keyword
        await tools_handler.add_task(title="Buy groceries")

        result = await tools_handler.list_tasks(search="groceries")

        assert result["success"] is True
        assert result["count"] >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
