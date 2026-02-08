# Skill: MCP Server Builder

## Purpose
Build Model Context Protocol (MCP) servers that expose application functionality as AI-callable tools using the Official MCP SDK.

## Tech Stack
- **MCP SDK**: Official Python SDK
- **FastAPI**: For HTTP server (if needed)
- **Pydantic**: For tool parameter validation

## What is MCP?

MCP (Model Context Protocol) is a standard way to expose tools/functions that AI agents can call. Instead of the AI just generating text, it can:
1. Call your `add_task` tool
2. Get the result back
3. Use it in its response

## MCP Architecture

```
┌─────────────┐         ┌─────────────────┐         ┌──────────────┐
│  AI Agent   │────────▶│   MCP Server    │────────▶│  Database    │
│ (OpenAI SDK)│  Calls  │  (Your Tools)   │  Exec   │  (Neon DB)   │
└─────────────┘  Tools  └─────────────────┘  Logic  └──────────────┘
                           │
                           ├─ add_task
                           ├─ list_tasks
                           ├─ complete_task
                           ├─ delete_task
                           └─ update_task
```

## Project Structure

```
backend/
├── mcp_server.py           # MCP server with tools
├── mcp_tools/
│   ├── __init__.py
│   ├── task_tools.py       # Task management tools
│   └── schemas.py          # Tool parameter schemas
├── models.py               # Database models
└── db.py                   # Database connection
```

## Building MCP Tools

### 1. Define Tool Schemas (Pydantic)

```python
"""
mcp_tools/schemas.py - Tool parameter schemas
[Task]: T-050
[From]: plan.md §7.2 - MCP Tools Specification
"""

from pydantic import BaseModel, Field
from typing import Optional

class AddTaskParams(BaseModel):
    """
    Parameters for add_task tool.
    
    [Spec]: specify.md §3.2 - Task Creation
    """
    user_id: str = Field(description="User ID who owns the task")
    title: str = Field(description="Task title (1-200 characters)")
    description: Optional[str] = Field(default=None, description="Optional task description (max 1000 chars)")

class ListTasksParams(BaseModel):
    """
    Parameters for list_tasks tool.
    
    [Spec]: specify.md §3.2 - View Tasks
    """
    user_id: str = Field(description="User ID to fetch tasks for")
    status: str = Field(default="all", description="Filter: 'all', 'pending', or 'completed'")

class CompleteTaskParams(BaseModel):
    """
    Parameters for complete_task tool.
    
    [Spec]: specify.md §3.2 - Mark Complete
    """
    user_id: str = Field(description="User ID who owns the task")
    task_id: int = Field(description="Task ID to mark complete")

class DeleteTaskParams(BaseModel):
    """
    Parameters for delete_task tool.
    
    [Spec]: specify.md §3.2 - Delete Task
    """
    user_id: str = Field(description="User ID who owns the task")
    task_id: int = Field(description="Task ID to delete")

class UpdateTaskParams(BaseModel):
    """
    Parameters for update_task tool.
    
    [Spec]: specify.md §3.2 - Update Task
    """
    user_id: str = Field(description="User ID who owns the task")
    task_id: int = Field(description="Task ID to update")
    title: Optional[str] = Field(default=None, description="New title")
    description: Optional[str] = Field(default=None, description="New description")
```

### 2. Implement MCP Tools

```python
"""
mcp_tools/task_tools.py - MCP tool implementations
[Task]: T-051
[From]: plan.md §7.2 - MCP Tools Specification
"""

from mcp.server import Server
from mcp.types import Tool, TextContent
from sqlmodel import select
from db import AsyncSession, get_session
from models import Task
from .schemas import AddTaskParams, ListTasksParams, CompleteTaskParams, DeleteTaskParams, UpdateTaskParams
import json
from datetime import datetime

# Initialize MCP server
mcp = Server("todo-mcp-server")

@mcp.tool()
async def add_task(params: AddTaskParams) -> str:
    """
    Create a new task for the user.
    
    [Task]: T-051-A
    [Spec]: specify.md §3.2 - Task Creation
    [MCP Tool]: add_task
    
    Args:
        params: AddTaskParams with user_id, title, description
        
    Returns:
        JSON string with task_id, status, and title
        
    Example:
        Input: {"user_id": "user123", "title": "Buy groceries", "description": "Milk and eggs"}
        Output: {"task_id": 5, "status": "created", "title": "Buy groceries"}
    """
    try:
        # Validation
        if not params.title or len(params.title) > 200:
            return json.dumps({"error": "Title must be 1-200 characters"})
        
        if params.description and len(params.description) > 1000:
            return json.dumps({"error": "Description max 1000 characters"})
        
        # Create task
        async with get_session() as session:
            task = Task(
                user_id=params.user_id,
                title=params.title,
                description=params.description,
                completed=False
            )
            
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            return json.dumps({
                "task_id": task.id,
                "status": "created",
                "title": task.title
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def list_tasks(params: ListTasksParams) -> str:
    """
    Retrieve user's tasks with optional filtering.
    
    [Task]: T-051-B
    [Spec]: specify.md §3.2 - View Tasks
    [MCP Tool]: list_tasks
    
    Args:
        params: ListTasksParams with user_id and status filter
        
    Returns:
        JSON array of task objects
        
    Example:
        Input: {"user_id": "user123", "status": "pending"}
        Output: [{"id": 1, "title": "Buy groceries", "completed": false}, ...]
    """
    try:
        async with get_session() as session:
            # Build query
            query = select(Task).where(Task.user_id == params.user_id)
            
            # Apply status filter
            if params.status == "pending":
                query = query.where(Task.completed == False)
            elif params.status == "completed":
                query = query.where(Task.completed == True)
            
            # Execute
            result = await session.execute(query)
            tasks = result.scalars().all()
            
            # Convert to dict
            tasks_data = [
                {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]
            
            return json.dumps(tasks_data)
            
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def complete_task(params: CompleteTaskParams) -> str:
    """
    Mark a task as complete.
    
    [Task]: T-051-C
    [Spec]: specify.md §3.2 - Mark Complete
    [MCP Tool]: complete_task
    
    Args:
        params: CompleteTaskParams with user_id and task_id
        
    Returns:
        JSON with task_id, status, and title
        
    Example:
        Input: {"user_id": "user123", "task_id": 3}
        Output: {"task_id": 3, "status": "completed", "title": "Call mom"}
    """
    try:
        async with get_session() as session:
            # Fetch task
            result = await session.execute(
                select(Task).where(
                    Task.id == params.task_id,
                    Task.user_id == params.user_id
                )
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return json.dumps({"error": "Task not found"})
            
            # Mark complete
            task.completed = True
            task.updated_at = datetime.utcnow()
            
            await session.commit()
            
            return json.dumps({
                "task_id": task.id,
                "status": "completed",
                "title": task.title
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def delete_task(params: DeleteTaskParams) -> str:
    """
    Remove a task from the list.
    
    [Task]: T-051-D
    [Spec]: specify.md §3.2 - Delete Task
    [MCP Tool]: delete_task
    
    Args:
        params: DeleteTaskParams with user_id and task_id
        
    Returns:
        JSON with task_id, status, and title
        
    Example:
        Input: {"user_id": "user123", "task_id": 2}
        Output: {"task_id": 2, "status": "deleted", "title": "Old task"}
    """
    try:
        async with get_session() as session:
            # Fetch task
            result = await session.execute(
                select(Task).where(
                    Task.id == params.task_id,
                    Task.user_id == params.user_id
                )
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return json.dumps({"error": "Task not found"})
            
            title = task.title
            
            # Delete
            await session.delete(task)
            await session.commit()
            
            return json.dumps({
                "task_id": params.task_id,
                "status": "deleted",
                "title": title
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.tool()
async def update_task(params: UpdateTaskParams) -> str:
    """
    Modify task title or description.
    
    [Task]: T-051-E
    [Spec]: specify.md §3.2 - Update Task
    [MCP Tool]: update_task
    
    Args:
        params: UpdateTaskParams with user_id, task_id, and fields to update
        
    Returns:
        JSON with task_id, status, and new title
        
    Example:
        Input: {"user_id": "user123", "task_id": 1, "title": "Buy groceries and fruits"}
        Output: {"task_id": 1, "status": "updated", "title": "Buy groceries and fruits"}
    """
    try:
        async with get_session() as session:
            # Fetch task
            result = await session.execute(
                select(Task).where(
                    Task.id == params.task_id,
                    Task.user_id == params.user_id
                )
            )
            task = result.scalar_one_or_none()
            
            if not task:
                return json.dumps({"error": "Task not found"})
            
            # Update fields
            if params.title is not None:
                if len(params.title) > 200:
                    return json.dumps({"error": "Title max 200 characters"})
                task.title = params.title
            
            if params.description is not None:
                if len(params.description) > 1000:
                    return json.dumps({"error": "Description max 1000 characters"})
                task.description = params.description
            
            task.updated_at = datetime.utcnow()
            
            await session.commit()
            
            return json.dumps({
                "task_id": task.id,
                "status": "updated",
                "title": task.title
            })
            
    except Exception as e:
        return json.dumps({"error": str(e)})
```

### 3. Run the MCP Server

```python
"""
mcp_server.py - MCP server entry point
[Task]: T-052
[From]: plan.md §7.1 - MCP Architecture
"""

from mcp_tools.task_tools import mcp
import asyncio

if __name__ == "__main__":
    # Run MCP server
    asyncio.run(mcp.run())
```

## Integrating with OpenAI Agents SDK

```python
"""
Chat endpoint that uses MCP tools
[Task]: T-053
[From]: plan.md §7.3 - Agent + MCP Integration
"""

from fastapi import APIRouter
from openai import OpenAI
from mcp_tools.task_tools import mcp

router = APIRouter()

@router.post("/api/{user_id}/chat")
async def chat(user_id: str, message: str, conversation_id: int = None):
    """
    Stateless chat endpoint using OpenAI Agents SDK + MCP tools.
    
    [Spec]: plan.md §7.3 - Stateless Chat Architecture
    """
    
    # 1. Fetch conversation history from database
    history = await get_conversation_history(conversation_id) if conversation_id else []
    
    # 2. Build messages array
    messages = history + [{"role": "user", "content": message}]
    
    # 3. Run agent with MCP tools
    client = OpenAI()
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=mcp.get_tools(),  # MCP tools as OpenAI tools
        tool_choice="auto"
    )
    
    # 4. Handle tool calls
    if response.choices[0].message.tool_calls:
        for tool_call in response.choices[0].message.tool_calls:
            # Execute MCP tool
            result = await mcp.call_tool(tool_call.function.name, tool_call.function.arguments)
            
            # Add tool result to messages
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })
        
        # Get final response
        final_response = client.chat.completions.create(
            model="gpt-4",
            messages=messages
        )
        
        assistant_message = final_response.choices[0].message.content
    else:
        assistant_message = response.choices[0].message.content
    
    # 5. Save messages to database
    await save_messages(conversation_id, user_id, message, assistant_message)
    
    return {
        "conversation_id": conversation_id,
        "response": assistant_message
    }
```

## Best Practices

### 1. Always Return JSON Strings
```python
# ✅ Good
return json.dumps({"task_id": 1, "status": "created"})

# ❌ Bad
return {"task_id": 1}  # MCP expects strings
```

### 2. Validate All Inputs
```python
# ✅ Good - Pydantic handles validation
class AddTaskParams(BaseModel):
    title: str = Field(min_length=1, max_length=200)

# ❌ Bad - No validation
def add_task(title: str):
    pass  # What if title is 500 characters?
```

### 3. Handle Errors Gracefully
```python
# ✅ Good
try:
    task = await create_task()
    return json.dumps({"success": True})
except Exception as e:
    return json.dumps({"error": str(e)})

# ❌ Bad - Let exceptions propagate
task = await create_task()  # Crashes the tool
```

## Testing MCP Tools

```python
# Test directly
import asyncio
from mcp_tools.task_tools import add_task
from mcp_tools.schemas import AddTaskParams

async def test():
    result = await add_task(AddTaskParams(
        user_id="test_user",
        title="Test task",
        description="Testing"
    ))
    print(result)

asyncio.run(test())
```

## Summary

This skill provides:
- ✅ MCP server setup with Official SDK
- ✅ Type-safe tool parameters (Pydantic)
- ✅ Database integration (async)
- ✅ Error handling
- ✅ OpenAI Agents SDK integration
- ✅ Stateless architecture
- ✅ Production-ready patterns