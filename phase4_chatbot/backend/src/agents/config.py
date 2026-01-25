"""Agent configuration and prompts."""

# System prompt for the todo assistant
SYSTEM_PROMPT = """You are a friendly and helpful todo assistant. Your role is to help users manage their tasks through natural language conversation.

Key behaviors:
1. Always confirm actions with friendly, natural responses
2. When adding a task, confirm with: "Task '[title]' added! [COMPLETED]"
3. When completing a task, confirm with: "Task [id] marked as complete! [DONE]"
4. When updating a task, confirm with: "Task [id] updated! [UPDATED]"
5. When deleting a task, confirm with: "Task [id] deleted. [REMOVED]"
6. When listing tasks, format them clearly with IDs and status groups
7. Handle errors gracefully with helpful messages like "I couldn't find task 5..." instead of error codes
8. If a task reference is ambiguous, ask for clarification by listing options with IDs
9. Stay on-topic: if asked non-task questions, politely redirect: "I'm a todo assistant. I can help you manage tasks. What would you like to do?"
10. Always be concise but friendly in your responses

Use the available tools to perform task operations. You have access to:
- add_task: Create new tasks
- list_tasks: Show tasks (filtered by status if needed)
- complete_task: Mark tasks as done
- update_task: Modify task properties
- delete_task: Remove tasks

When the user asks about their tasks, use list_tasks to fetch current state before suggesting actions.
"""

# Agent configuration
AGENT_CONFIG = {
    "model": "command-r-v4",
    "temperature": 0.7,
    "max_tokens": 1024,
    "tool_choice": "auto",
    "system_prompt": SYSTEM_PROMPT,
}

# Tool definitions for MCP
TOOL_DEFINITIONS = [
    {
        "name": "add_task",
        "description": "Create a new task for the authenticated user",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (max 255 characters)",
                },
                "description": {
                    "type": "string",
                    "description": "Task description (optional, max 2000 characters)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Task priority (default: medium)",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in ISO 8601 format (optional)",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_tasks",
        "description": "Retrieve tasks for the authenticated user with optional filtering",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter by status (default: all)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "all"],
                    "description": "Filter by priority (default: all)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task as complete for the authenticated user",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of task to complete",
                },
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "update_task",
        "description": "Modify task properties for the authenticated user",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of task to update",
                },
                "title": {
                    "type": "string",
                    "description": "New title (optional)",
                },
                "description": {
                    "type": "string",
                    "description": "New description (optional)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "New priority (optional)",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed"],
                    "description": "New status (optional)",
                },
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "delete_task",
        "description": "Remove a task for the authenticated user",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "ID of task to delete",
                },
            },
            "required": ["task_id"],
        },
    },
]
