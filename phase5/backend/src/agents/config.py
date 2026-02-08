"""Agent configuration and prompts.

Phase V Part A: Enhanced with priority, tags, search, filter, sort, recurrence,
due dates, and reminder recognition patterns.
"""

# System prompt for the todo assistant
SYSTEM_PROMPT = """You are a friendly and helpful todo assistant. Your role is to help users manage their tasks through natural language conversation.

## Key Behaviors

1. Always confirm actions with friendly, natural responses
2. When adding a task, confirm with details: "Task '[title]' added with priority [PRIORITY], tagged [tags], due [date]!"
3. When completing a task, confirm with: "Task [id] marked as complete! [DONE]"
4. When updating a task, confirm with what changed: "Task [id] updated: [changes]"
5. When deleting a task, confirm with: "Task [id] deleted. [REMOVED]"
6. When listing tasks, format them clearly with IDs, priority badges, tags, and due dates
7. Handle errors gracefully with helpful messages
8. If a task reference is ambiguous, ask for clarification by listing options with IDs
9. Stay on-topic: redirect non-task questions politely
10. Always be concise but friendly

## Available Tools

- add_task: Create new tasks with priority, tags, due dates, reminders, and recurrence
- list_tasks: Show tasks with filtering by status, priority, tags, keyword search, and sorting
- complete_task: Mark tasks as done (creates next occurrence for recurring tasks)
- update_task: Modify task properties including recurrence and reminders
- delete_task: Remove tasks

## Intent Recognition Patterns

### PRIORITY RECOGNITION
- "high priority", "urgent", "important", "critical", "asap" → priority="high"
- "medium priority", "normal", "regular" → priority="medium"
- "low priority", "minor", "can wait", "eventually" → priority="low"

### TAG RECOGNITION
- "tagged X", "tag X", "with tag X", "label X", "category X" → tags=["X"]
- "tagged X and Y", "tags X, Y", "labels X Y" → tags=["X", "Y"]

### SEARCH & FILTER RECOGNITION
- "find X", "search for X", "look for X", "containing X" → search="X"
- "show only high priority", "filter by high" → priority="high"
- "show tasks tagged X", "filter by tag X" → tag="X"
- "pending tasks", "incomplete tasks", "todo" → status="pending"
- "completed tasks", "done tasks", "finished" → status="completed"

### SORT RECOGNITION
- "sort by due date", "order by deadline", "by due date" → sort="due_date"
- "sort by priority", "most important first" → sort="priority", order="desc"
- "sort by created", "oldest first" → sort="created_at", order="asc"
- "newest first", "most recent" → sort="created_at", order="desc"
- "alphabetical", "by name", "by title" → sort="title", order="asc"

### RECURRENCE RECOGNITION
- "repeat daily", "every day", "daily" → recurrence={"type": "daily", "interval": 1}
- "repeat weekly", "every week", "weekly" → recurrence={"type": "weekly", "interval": 1}
- "every 2 weeks", "biweekly" → recurrence={"type": "weekly", "interval": 2}
- "repeat monthly", "every month", "monthly" → recurrence={"type": "monthly", "interval": 1}
- "until DATE", "ending DATE", "stop on DATE" → add end_date to recurrence

### DUE DATE RECOGNITION
- "due tomorrow", "by tomorrow" → calculate tomorrow's date
- "due Friday", "by Friday", "on Friday" → calculate next Friday
- "due in 3 days", "in 3 days" → calculate date + 3 days
- "due next week" → calculate 7 days from now
- "due end of month" → calculate last day of current month

### REMINDER RECOGNITION
- "remind me 15 minutes before" → reminder_offset_minutes=15
- "remind me 30 minutes before" → reminder_offset_minutes=30
- "remind me 1 hour before", "remind me an hour before" → reminder_offset_minutes=60
- "remind me 1 day before", "remind me a day before" → reminder_offset_minutes=1440
- "no reminder" → reminder_offset_minutes=null

## Example Interactions

User: "add high priority task meeting due Friday tagged work"
→ Call add_task with title="meeting", priority="high", due_date=<next_friday>, tags=["work"]

User: "show pending tasks tagged work sorted by due date"
→ Call list_tasks with status="pending", tag="work", sort="due_date"

User: "add task weekly standup repeat weekly remind me 30 minutes before"
→ Call add_task with title="weekly standup", recurrence={"type": "weekly", "interval": 1}, reminder_offset_minutes=30

User: "find tasks about groceries"
→ Call list_tasks with search="groceries"

User: "make task 5 repeat daily until end of March"
→ Call update_task with task_id="5", recurrence={"type": "daily", "interval": 1, "end_date": "<march_31>"}

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
        "description": "Create a new task. Supports priority levels (high/medium/low), tags for categorization, due dates, reminders, and recurring schedules (daily/weekly/monthly).",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (required, max 255 characters)",
                },
                "description": {
                    "type": "string",
                    "description": "Task description (optional, max 2000 characters)",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "none"],
                    "description": "Task priority level. Use 'high' for urgent tasks, 'medium' for normal, 'low' for minor tasks.",
                },
                "due_date": {
                    "type": "string",
                    "description": "Due date in ISO 8601 format (e.g., '2026-02-15T17:00:00Z') or relative like 'tomorrow', 'next Friday'.",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Category tags for the task (e.g., ['work', 'personal', 'urgent']). Max 10 tags.",
                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "type": {
                            "type": "string",
                            "enum": ["daily", "weekly", "monthly"],
                            "description": "How often the task repeats.",
                        },
                        "interval": {
                            "type": "integer",
                            "description": "Number of periods between occurrences. Default 1.",
                        },
                        "end_date": {
                            "type": "string",
                            "description": "When recurrence stops. ISO 8601 format.",
                        },
                    },
                    "description": "Make the task recurring. Set type to 'daily', 'weekly', or 'monthly'.",
                },
                "reminder_offset_minutes": {
                    "type": "integer",
                    "description": "Remind user this many minutes before due_date. E.g., 60 for 1 hour before, 1440 for 1 day before.",
                },
            },
            "required": ["title"],
        },
    },
    {
        "name": "list_tasks",
        "description": "List tasks with filtering by status, priority, tags, and keyword search. Supports sorting by various fields. Use this to show, find, or search for tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed", "all"],
                    "description": "Filter by status: 'pending' for incomplete, 'completed' for done, 'all' for everything.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "none", "all"],
                    "description": "Filter to show only tasks with this priority level.",
                },
                "tag": {
                    "type": "string",
                    "description": "Filter to show only tasks with this tag. Example: 'work' to show work-related tasks.",
                },
                "search": {
                    "type": "string",
                    "description": "Search keyword to find in task titles or descriptions. Example: 'meeting' to find meeting-related tasks.",
                },
                "sort": {
                    "type": "string",
                    "enum": ["created_at", "due_date", "priority", "title", "updated_at"],
                    "description": "Field to sort results by. Default is 'created_at'.",
                },
                "order": {
                    "type": "string",
                    "enum": ["asc", "desc"],
                    "description": "Sort order: 'asc' for ascending (oldest/lowest first), 'desc' for descending (newest/highest first).",
                },
            },
            "required": [],
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task as complete/done. If the task is recurring, a new occurrence will be created automatically with the next due date.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID number of the task to mark as complete.",
                },
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "update_task",
        "description": "Modify task properties including priority, tags, recurrence, due dates, and reminders. Use this to change, edit, or update existing tasks.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID number of the task to update (required).",
                },
                "title": {
                    "type": "string",
                    "description": "New title for the task.",
                },
                "description": {
                    "type": "string",
                    "description": "New description for the task.",
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high", "none"],
                    "description": "New priority level for the task.",
                },
                "status": {
                    "type": "string",
                    "enum": ["pending", "completed"],
                    "description": "New status. Use 'completed' to mark done, 'pending' to reopen.",
                },
                "due_date": {
                    "type": "string",
                    "description": "New due date. ISO 8601 format or relative like 'tomorrow'.",
                },
                "tags": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "New tags for the task. Replaces existing tags.",
                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "type": {"type": "string", "enum": ["daily", "weekly", "monthly"]},
                        "interval": {"type": "integer"},
                        "end_date": {"type": "string"},
                    },
                    "description": "New recurrence settings. Set to make task repeat, or null to stop recurring.",
                },
                "reminder_offset_minutes": {
                    "type": "integer",
                    "description": "New reminder offset in minutes before due date.",
                },
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "delete_task",
        "description": "Permanently delete a task. This action cannot be undone.",
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {
                    "type": "string",
                    "description": "The ID number of the task to delete.",
                },
            },
            "required": ["task_id"],
        },
    },
]
