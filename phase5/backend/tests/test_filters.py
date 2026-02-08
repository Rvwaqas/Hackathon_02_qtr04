"""
Unit tests for Phase V Part A - Advanced Filtering and Sorting.

Tests cover:
- Priority filtering (T542)
- Tag filtering (T543)
- Keyword search (T544)
- Sort by due_date (T545)
- Sort by priority (T546)
- Combined filters (T547)
"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from src.mcp.tools import TodoToolsHandler
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


@pytest.fixture(autouse=True)
def mock_event_publishing():
    """Mock event publisher to prevent real HTTP calls (autouse for all filter tests)."""
    with patch("src.services.event_publisher.EventPublisher.publish", new_callable=AsyncMock, return_value=True):
        yield


@pytest_asyncio.fixture
async def tools_handler(async_session):
    """Create TodoToolsHandler instance."""
    return TodoToolsHandler(async_session, user_id="1")


@pytest_asyncio.fixture
async def seeded_tasks(tools_handler):
    """Seed test database with diverse tasks for filtering tests."""
    tasks = [
        # High priority work tasks
        {"title": "Quarterly report", "priority": "high", "tags": ["work", "reports"]},
        {"title": "Team meeting", "priority": "high", "tags": ["work", "meetings"]},
        # Medium priority tasks
        {"title": "Code review", "priority": "medium", "tags": ["work", "dev"]},
        {"title": "Buy groceries", "priority": "medium", "tags": ["personal", "shopping"]},
        # Low priority tasks
        {"title": "Organize desk", "priority": "low", "tags": ["personal"]},
        {"title": "Read article about meetings", "priority": "low", "tags": ["learning"]},
    ]

    created_ids = []
    for task_data in tasks:
        result = await tools_handler.add_task(**task_data)
        created_ids.append(result["task_id"])

    return created_ids


# ============ T542: Priority Filter Tests ============

@pytest.mark.asyncio
async def test_filter_high_priority(tools_handler, seeded_tasks):
    """T542: Filter to show only high priority tasks."""
    result = await tools_handler.list_tasks(priority="high")

    assert result["success"] is True
    assert result["count"] == 2
    for task in result["tasks"]:
        assert task["priority"] == "high"


@pytest.mark.asyncio
async def test_filter_medium_priority(tools_handler, seeded_tasks):
    """T542: Filter to show only medium priority tasks."""
    result = await tools_handler.list_tasks(priority="medium")

    assert result["success"] is True
    assert result["count"] == 2
    for task in result["tasks"]:
        assert task["priority"] == "medium"


@pytest.mark.asyncio
async def test_filter_low_priority(tools_handler, seeded_tasks):
    """T542: Filter to show only low priority tasks."""
    result = await tools_handler.list_tasks(priority="low")

    assert result["success"] is True
    assert result["count"] == 2
    for task in result["tasks"]:
        assert task["priority"] == "low"


# ============ T543: Tag Filter Tests ============

@pytest.mark.asyncio
async def test_filter_by_tag_work(tools_handler, seeded_tasks):
    """T543: Filter tasks by 'work' tag."""
    result = await tools_handler.list_tasks(tag="work")

    assert result["success"] is True
    assert result["count"] == 3  # quarterly report, team meeting, code review
    for task in result["tasks"]:
        assert "work" in task["tags"]


@pytest.mark.asyncio
async def test_filter_by_tag_personal(tools_handler, seeded_tasks):
    """T543: Filter tasks by 'personal' tag."""
    result = await tools_handler.list_tasks(tag="personal")

    assert result["success"] is True
    assert result["count"] == 2  # groceries, organize desk
    for task in result["tasks"]:
        assert "personal" in task["tags"]


@pytest.mark.asyncio
async def test_filter_by_tag_no_results(tools_handler, seeded_tasks):
    """T543: Filter by tag that doesn't exist."""
    result = await tools_handler.list_tasks(tag="nonexistent")

    assert result["success"] is True
    assert result["count"] == 0
    assert "No tasks found" in result["message"]


# ============ T544: Search by Keyword Tests ============

@pytest.mark.asyncio
async def test_search_by_keyword_title(tools_handler, seeded_tasks):
    """T544: Search for keyword in task titles."""
    result = await tools_handler.list_tasks(search="meeting")

    assert result["success"] is True
    assert result["count"] == 2  # Team meeting + article about meetings
    for task in result["tasks"]:
        assert "meeting" in task["title"].lower()


@pytest.mark.asyncio
async def test_search_by_keyword_partial(tools_handler, seeded_tasks):
    """T544: Search with partial keyword."""
    result = await tools_handler.list_tasks(search="report")

    assert result["success"] is True
    assert result["count"] == 1
    assert "report" in result["tasks"][0]["title"].lower()


@pytest.mark.asyncio
async def test_search_case_insensitive(tools_handler, seeded_tasks):
    """T544: Search should be case insensitive."""
    result = await tools_handler.list_tasks(search="QUARTERLY")

    assert result["success"] is True
    assert result["count"] == 1


@pytest.mark.asyncio
async def test_search_no_results(tools_handler, seeded_tasks):
    """T544: Search with no matching results."""
    result = await tools_handler.list_tasks(search="xyznotfound")

    assert result["success"] is True
    assert result["count"] == 0


# ============ T545: Sort by Due Date Tests ============

@pytest.mark.asyncio
async def test_sort_by_due_date_asc(tools_handler):
    """T545: Sort tasks by due date ascending."""
    # Create tasks with different due dates
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    next_week = (datetime.utcnow() + timedelta(days=7)).isoformat()
    today = datetime.utcnow().isoformat()

    await tools_handler.add_task(title="Due next week", due_date=next_week)
    await tools_handler.add_task(title="Due tomorrow", due_date=tomorrow)
    await tools_handler.add_task(title="Due today", due_date=today)

    result = await tools_handler.list_tasks(sort="due_date", order="asc")

    assert result["success"] is True
    assert result["count"] == 3
    # Verify order: today < tomorrow < next week
    assert result["tasks"][0]["title"] == "Due today"
    assert result["tasks"][1]["title"] == "Due tomorrow"
    assert result["tasks"][2]["title"] == "Due next week"


@pytest.mark.asyncio
async def test_sort_by_due_date_desc(tools_handler):
    """T545: Sort tasks by due date descending."""
    tomorrow = (datetime.utcnow() + timedelta(days=1)).isoformat()
    next_week = (datetime.utcnow() + timedelta(days=7)).isoformat()
    today = datetime.utcnow().isoformat()

    await tools_handler.add_task(title="Due today", due_date=today)
    await tools_handler.add_task(title="Due next week", due_date=next_week)
    await tools_handler.add_task(title="Due tomorrow", due_date=tomorrow)

    result = await tools_handler.list_tasks(sort="due_date", order="desc")

    assert result["success"] is True
    # Verify order: next week > tomorrow > today
    assert result["tasks"][0]["title"] == "Due next week"
    assert result["tasks"][1]["title"] == "Due tomorrow"
    assert result["tasks"][2]["title"] == "Due today"


# ============ T546: Sort by Priority Tests ============

@pytest.mark.asyncio
async def test_sort_by_priority_desc(tools_handler, seeded_tasks):
    """T546: Sort tasks by priority descending."""
    result = await tools_handler.list_tasks(sort="priority", order="desc")

    assert result["success"] is True
    assert result["count"] == 6
    # Verify tasks are sorted by priority (string sort: none > medium > low > high)
    priorities = [t["priority"] for t in result["tasks"]]
    assert priorities == sorted(priorities, reverse=True)


@pytest.mark.asyncio
async def test_sort_by_priority_asc(tools_handler, seeded_tasks):
    """T546: Sort tasks by priority ascending."""
    result = await tools_handler.list_tasks(sort="priority", order="asc")

    assert result["success"] is True
    assert result["count"] == 6
    # Verify tasks are sorted by priority ascending
    priorities = [t["priority"] for t in result["tasks"]]
    assert priorities == sorted(priorities)


# ============ T547: Combined Filters Tests ============

@pytest.mark.asyncio
async def test_combined_status_and_priority(tools_handler, seeded_tasks):
    """T547: Filter by status AND priority."""
    result = await tools_handler.list_tasks(
        status="pending",
        priority="high"
    )

    assert result["success"] is True
    assert result["count"] == 2
    for task in result["tasks"]:
        assert task["status"] == "pending"
        assert task["priority"] == "high"


@pytest.mark.asyncio
async def test_combined_priority_and_tag(tools_handler, seeded_tasks):
    """T547: Filter by priority AND tag."""
    result = await tools_handler.list_tasks(
        priority="high",
        tag="work"
    )

    assert result["success"] is True
    assert result["count"] == 2  # quarterly report, team meeting
    for task in result["tasks"]:
        assert task["priority"] == "high"
        assert "work" in task["tags"]


@pytest.mark.asyncio
async def test_combined_tag_and_search(tools_handler, seeded_tasks):
    """T547: Filter by tag AND search keyword."""
    result = await tools_handler.list_tasks(
        tag="work",
        search="meeting"
    )

    assert result["success"] is True
    assert result["count"] == 1  # only Team meeting has both work tag and meeting in title


@pytest.mark.asyncio
async def test_combined_all_filters_and_sort(tools_handler, seeded_tasks):
    """T547: Apply status, priority, tag, and sort together."""
    result = await tools_handler.list_tasks(
        status="pending",
        priority="high",
        tag="work",
        sort="title",
        order="asc"
    )

    assert result["success"] is True
    # Should get: Quarterly report, Team meeting (both high+work+pending)
    assert result["count"] == 2
    # Sorted alphabetically by title
    assert result["tasks"][0]["title"] == "Quarterly report"
    assert result["tasks"][1]["title"] == "Team meeting"


@pytest.mark.asyncio
async def test_combined_filters_no_results(tools_handler, seeded_tasks):
    """T547: Combined filters that yield no results."""
    result = await tools_handler.list_tasks(
        priority="high",
        tag="personal"  # No high priority personal tasks
    )

    assert result["success"] is True
    assert result["count"] == 0
    assert "No tasks found" in result["message"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
