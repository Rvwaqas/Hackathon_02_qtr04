# Setup MCP Server

Use the Official MCP Python SDK to create a stateless MCP server integrated with FastAPI.

## Core Requirements

### 5 Required Tools

| Tool | Parameters | Returns |
|------|-----------|---------|
| `add_task` | user_id, title, description? | `{success, task_id, message}` |
| `list_tasks` | user_id, status? | `{success, tasks[], count}` |
| `get_task` | user_id, task_id | `{success, task}` |
| `update_task` | user_id, task_id, title?, description?, status? | `{success, task, message}` |
| `delete_task` | user_id, task_id | `{success, message}` |

### Tool Signatures

```python
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

server = Server("todo-mcp-server")

@server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    """Add a new task for the user."""
    # SQLModel DB operation
    pass

@server.tool()
async def list_tasks(user_id: str, status: str = "all") -> dict:
    """List tasks for the user. Status: all, pending, completed."""
    pass

@server.tool()
async def get_task(user_id: str, task_id: int) -> dict:
    """Get a specific task by ID."""
    pass

@server.tool()
async def update_task(user_id: str, task_id: int, **updates) -> dict:
    """Update task fields (title, description, status)."""
    pass

@server.tool()
async def delete_task(user_id: str, task_id: int) -> dict:
    """Delete a task by ID."""
    pass
```

## Stateless Architecture

### User Isolation
- Every tool MUST accept `user_id` as first parameter
- Extract `user_id` from JWT token at API layer
- Pass to MCP tools - no session state
- Query DB filtered by user_id always

### No In-Memory State
```python
# WRONG - storing state
tasks_cache = {}  # ❌ Never do this

# RIGHT - always query DB
async def list_tasks(user_id: str, status: str = "all"):
    async with get_session() as session:
        query = select(Task).where(Task.user_id == user_id)
        # ... execute and return
```

## SQLModel Integration

```python
from sqlmodel import SQLModel, Field, Session, select
from database import get_session

class Task(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    title: str
    description: str = ""
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

## Response Format (Hackathon Spec)

```json
// Success - add_task
{
  "success": true,
  "task_id": 123,
  "message": "Task created successfully"
}

// Success - list_tasks
{
  "success": true,
  "tasks": [
    {"id": 1, "title": "Buy milk", "status": "pending"},
    {"id": 2, "title": "Call mom", "status": "completed"}
  ],
  "count": 2
}

// Error
{
  "success": false,
  "error": "Task not found",
  "error_code": "TASK_NOT_FOUND"
}
```

## Tool Chaining

Handle sequences gracefully:
```python
# User: "Delete my completed tasks"
# 1. list_tasks(user_id, status="completed")
# 2. For each task: delete_task(user_id, task_id)

# Return combined result
{
  "success": true,
  "message": "Deleted 3 completed tasks",
  "deleted_ids": [5, 8, 12]
}
```

## Logging

```python
import logging

logger = logging.getLogger("mcp-tools")

@server.tool()
async def add_task(user_id: str, title: str, description: str = "") -> dict:
    logger.info(f"add_task called: user={user_id}, title={title}")
    try:
        # ... implementation
        logger.info(f"add_task success: task_id={task.id}")
        return {"success": True, "task_id": task.id}
    except Exception as e:
        logger.error(f"add_task failed: {e}")
        return {"success": False, "error": str(e)}
```

## FastAPI Integration

```python
from fastapi import FastAPI, Depends
from mcp.server.fastapi import create_mcp_router

app = FastAPI()

# Mount MCP server
mcp_router = create_mcp_router(server)
app.include_router(mcp_router, prefix="/mcp")

# Or manual endpoint
@app.post("/api/{user_id}/chat")
async def chat(user_id: str, request: ChatRequest):
    # Extract user_id from JWT
    # Pass to agent runner with MCP tools
    pass
```

## Checklist

- [ ] 5 tools implemented with exact signatures
- [ ] All tools accept user_id parameter
- [ ] SQLModel for all DB operations
- [ ] Neon PostgreSQL connection configured
- [ ] Structured JSON responses match spec
- [ ] Tool call logging enabled
- [ ] No in-memory state - fully stateless
- [ ] Error handling returns proper format
