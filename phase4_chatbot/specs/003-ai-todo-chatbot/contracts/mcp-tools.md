# MCP Tools Contract: Todo Task Management

**Purpose**: Define the 5 MCP tools that the agent uses to manage tasks

**Framework**: Official MCP SDK (Python)

**Status**: Proposal (Phase 1 design output)

---

## Tool 1: add_task

**Description**: Create a new task for the authenticated user

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | ✅ yes | Authenticated user ID (required for isolation) |
| `title` | string | ✅ yes | Task title (max 255 characters) |
| `description` | string | ❌ no | Task description (max 2000 characters) |
| `priority` | enum | ❌ no | Task priority: "low", "medium", "high" (default: "medium") |
| `due_date` | string (ISO 8601) | ❌ no | Due date for task (e.g., "2026-01-20") |

**Returns**:

```json
{
  "success": true,
  "task_id": "task-42",
  "message": "Task 'Buy groceries' created successfully"
}
```

**Error Responses**:

```json
{
  "success": false,
  "error": "invalid_input",
  "message": "Title is required"
}
```

**Implementation Notes**:
- Calls existing `TaskService.create_task(user_id, title, description, priority, due_date)`
- Validates title is non-empty and user_id is valid
- Returns task_id for potential subsequent references

---

## Tool 2: list_tasks

**Description**: Retrieve tasks for the authenticated user with optional filtering

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | ✅ yes | Authenticated user ID (required for isolation) |
| `status` | enum | ❌ no | Filter by status: "pending", "completed", or "all" (default: "all") |
| `priority` | enum | ❌ no | Filter by priority: "low", "medium", "high", or "all" (default: "all") |

**Returns**:

```json
{
  "success": true,
  "tasks": [
    {
      "id": "1",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "status": "pending",
      "priority": "medium",
      "created_at": "2026-01-15T10:00:00Z"
    },
    {
      "id": "2",
      "title": "Review PR",
      "status": "completed",
      "priority": "high",
      "created_at": "2026-01-14T15:30:00Z"
    }
  ],
  "count": 2
}
```

**Error Responses**:

```json
{
  "success": false,
  "error": "invalid_filter",
  "message": "Invalid status value: 'invalid_status'"
}
```

**Implementation Notes**:
- Calls `TaskService.get_tasks(user_id, status=status, priority=priority)`
- Returns all tasks if no filters specified
- Format response with task IDs and status for agent readability
- Agent uses this to understand current state before completing/updating/deleting

---

## Tool 3: complete_task

**Description**: Mark a task as complete for the authenticated user

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | ✅ yes | Authenticated user ID (required for isolation) |
| `task_id` | string | ✅ yes | ID of task to complete |

**Returns**:

```json
{
  "success": true,
  "task_id": "1",
  "message": "Task 'Buy groceries' marked as complete"
}
```

**Error Responses**:

```json
{
  "success": false,
  "error": "not_found",
  "message": "Task 1 not found"
}
```

```json
{
  "success": false,
  "error": "already_completed",
  "message": "Task 1 is already completed"
}
```

**Implementation Notes**:
- Calls `TaskService.update_task(user_id, task_id, status="completed")`
- Validates task_id exists and belongs to user_id
- Returns error if task already completed
- Agent handles errors gracefully (e.g., "I couldn't find task 5...")

---

## Tool 4: update_task

**Description**: Modify task properties for the authenticated user

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | ✅ yes | Authenticated user ID (required for isolation) |
| `task_id` | string | ✅ yes | ID of task to update |
| `title` | string | ❌ no | New title (if updating) |
| `description` | string | ❌ no | New description (if updating) |
| `priority` | enum | ❌ no | New priority: "low", "medium", "high" |
| `status` | enum | ❌ no | New status: "pending", "completed" |

**Returns**:

```json
{
  "success": true,
  "task_id": "2",
  "message": "Task 'Review PR' updated successfully"
}
```

**Error Responses**:

```json
{
  "success": false,
  "error": "not_found",
  "message": "Task 2 not found"
}
```

```json
{
  "success": false,
  "error": "invalid_input",
  "message": "At least one field must be updated"
}
```

**Implementation Notes**:
- Calls `TaskService.update_task(user_id, task_id, **update_fields)`
- Validates at least one field is provided for update
- Returns updated task with new values
- Agent uses this for reprioritization, rename, etc.

---

## Tool 5: delete_task

**Description**: Remove a task for the authenticated user

**Parameters**:

| Name | Type | Required | Description |
|------|------|----------|-------------|
| `user_id` | string | ✅ yes | Authenticated user ID (required for isolation) |
| `task_id` | string | ✅ yes | ID of task to delete |

**Returns**:

```json
{
  "success": true,
  "task_id": "3",
  "message": "Task 'Old project' deleted successfully"
}
```

**Error Responses**:

```json
{
  "success": false,
  "error": "not_found",
  "message": "Task 3 not found"
}
```

**Implementation Notes**:
- Calls `TaskService.delete_task(user_id, task_id)`
- Validates task_id exists and belongs to user_id
- Returns confirmation with deleted task_id
- Deletion is permanent (no soft delete)

---

## Tool Registration (Agent Setup)

All tools are registered with the Cohere agent via OpenAI Agents SDK:

```python
from openai import AsyncOpenAI
from openai.types.shared_params.function_definition import FunctionDefinition

client = AsyncOpenAI(
    api_key=os.getenv("COHERE_API_KEY"),
    base_url="https://api.cohere.com/v1"
)

tools = [
    FunctionDefinition(
        name="add_task",
        description="Create a new task for the authenticated user",
        parameters={
            "type": "object",
            "properties": {
                "user_id": {"type": "string", "description": "Authenticated user ID"},
                "title": {"type": "string", "description": "Task title (max 255 chars)"},
                "description": {"type": "string", "description": "Task description (optional)"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"]},
                "due_date": {"type": "string", "description": "ISO 8601 date format"}
            },
            "required": ["user_id", "title"]
        }
    ),
    # ... (similar for other 4 tools)
]

response = await client.chat.completions.create(
    model="command-r-plus",
    messages=conversation_history,
    tools=tools,
    tool_choice="auto"
)
```

---

## Tool Execution Flow

```
User Message
    ↓
Agent (Cohere LLM)
    ↓
    ├─ Understand Intent
    ├─ Select Tool(s)
    ├─ Extract Parameters
    └─ Call Tool
         ↓
      MCP Tool Handler
         ├─ Validate Inputs
         ├─ Check user_id authorization
         ├─ Call TaskService
         ├─ Handle Errors
         └─ Return Result
            ↓
         Agent Continues
         (tool result fed back to LLM)
            ↓
         Agent Generates Response
            ↓
         Return to User
```

---

## Error Handling Strategy

**Tool errors are caught and handled by the agent**:

- Agent receives tool error response
- Agent reformulates response for user
- User never sees raw error messages

**Examples**:
- Tool error: "Task 999 not found"
- Agent response: "I couldn't find task 999 in your tasks. Would you like me to list your tasks?"

---

## User Isolation Guarantee

**CRITICAL**: Every tool MUST validate that `user_id` matches the authenticated user:

```python
def add_task(user_id: str, title: str, ...) -> dict:
    # Validate user_id is authenticated user
    if user_id != request.user_id:
        return {"success": false, "error": "unauthorized"}

    # Proceed with operation
    task = TaskService.create_task(user_id, title, ...)
    return {"success": true, "task_id": task.id}
```

**Rule**: No tool can operate on a task unless the authenticated user_id matches the task's user_id.

---

## Testing Strategy

**Unit Tests**:
- Test each tool independently with mock TaskService
- Test error conditions (missing fields, invalid IDs)
- Test user isolation (user A cannot access user B's tasks)

**Integration Tests**:
- Test tools in combination with agent
- Test multi-tool workflows ("list tasks" → "complete first one")
- Test error recovery (agent handles tool errors gracefully)

**Contract Tests**:
- Verify tool signatures match expectations
- Verify return values match contract
- Verify parameter validation

---

## Future Tool Enhancements (Out of Scope)

- Bulk operations (complete multiple tasks)
- Task search (by keyword)
- Task tagging/categorization
- Task assignment (if multi-user collaboration added)
- Task dependencies/ordering
- Recurring tasks

