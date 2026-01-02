# Phase I: Console Todo App

Simple command-line todo application with in-memory storage demonstrating spec-driven development.

## Overview

This is Phase I of the "Evolution of Todo" hackathon project. It provides a basic task management CLI application with CRUD operations (Create, Read, Update, Delete) using in-memory storage.

## Requirements

- Python 3.13+
- UV package manager

## Setup

```bash
# Navigate to phase1 directory
cd phase1

# Sync dependencies (none required for Phase I)
uv sync
```

## Usage

```bash
# Run the application
python src/main.py
```

## Features

### Basic Features

#### 1. Add Task
Create a new task with a title and optional description.
- Title: Required, 1-200 characters
- Description: Optional, max 1000 characters
- Auto-assigned unique ID with default priority ("none") and tags ([])
- Confirmation message shows task ID

#### 2. View All Tasks
Display all tasks ordered by creation time (newest first).
- Shows: Priority indicator ([H]/[M]/[L]), ID, title, status (pending/completed), tags (#tag)
- Visual indicators: [X] for completed, [ ] for pending
- Priority indicators: [H] for high, [M] for medium, [L] for low, no indicator for none
- Tags displayed with # prefix (e.g., #work #urgent)
- Empty list shows friendly message

#### 3. Update Task
Modify task title or description.
- Enter task ID
- Provide new title and/or description
- Shows before/after confirmation
- Error message if task not found

#### 4. Delete Task
Remove a task from the list.
- Enter task ID
- Confirms deletion with y/n prompt
- Shows success or error message

#### 5. Mark Complete/Incomplete
Toggle task completion status.
- Enter task ID
- Status toggles between pending ↔ completed
- Visual indicator updates

### Intermediate Features (Organization & Discovery)

#### 6. Set Priority
Assign priority level to tasks for better organization.
- Priority levels: high, medium, low, none
- Visual indicators: [H], [M], [L] displayed before task title
- Helps identify important tasks at a glance
- Priority persists across views and filters

#### 7. Manage Tags
Categorize tasks with custom tags.
- Add up to 5 tags per task
- Tags must be alphanumeric, 1-20 characters each
- Stored as lowercase for consistency
- Duplicate tags automatically prevented
- Remove tags by name
- Tags displayed with # prefix (e.g., #work #personal #urgent)

#### 8. Search Tasks
Find tasks quickly by keyword.
- Case-insensitive search in title and description
- Shows count of matching tasks
- Empty keyword returns all tasks
- Results sorted by creation date (newest first)

#### 9. Filter Tasks
View specific subsets of tasks by criteria.
- Filter by status: all, pending, completed
- Filter by priority: high, medium, low, none
- Filter by tag: specify tag name
- Combined filters: apply multiple criteria with AND logic
- Shows "X of Y tasks" count
- "No tasks found" message for empty results

#### 10. Sort Tasks
Reorder tasks by different criteria.
- Sort by created date: newest or oldest first
- Sort by title: A-Z or Z-A (case-insensitive)
- Sort by priority: high→low or low→high
- Sort by status: pending/completed
- Header shows current sort criteria

### Advanced Features (Automation & Time Management)

#### 11. Set Recurrence
Make tasks repeat automatically on a schedule.
- Recurrence types: daily, weekly, monthly, none
- When recurring task is marked complete, next occurrence is automatically created
- Next occurrence inherits title, description, priority, tags (but resets completion status)
- Display indicator: "Recurring: Daily" or "Recurring: Weekly (Mon, Wed)"
- Handles month-end edge cases (Jan 31 → Feb 28/29)

#### 12. Set Due Date
Assign deadlines to tasks with countdown display.
- Format: YYYY-MM-DD HH:MM
- Must be future date (validation enforced)
- Display format: "Due: Jan 3, 2026 9:00 AM (in 2 days)"
- Overdue tasks shown in red with emphasis: "OVERDUE by 3 hours"
- Filter by overdue, due_today, due_this_week
- Sort by due date (earliest first)

#### 13. Set Reminder
Receive notifications before due dates.
- Reminder offsets: 15 minutes, 1 hour, 1 day, 1 week before due
- Requires task to have due date
- Background thread checks every 60 seconds
- CLI notification: "⏰ REMINDER: '[task]' is due soon!"
- Snooze option: Postpone for 10 minutes
- View option: See task details from notification
- Prevents duplicate notifications (marks as notified)

#### 14. View Overdue Tasks
Quick view of tasks past their due date.
- Filters to show only overdue tasks
- Displays in red with overdue duration: "OVERDUE by 2 days"
- Sorted by due date (earliest overdue first)

#### 15. View Upcoming (7 days)
See tasks due in the next week.
- Filters tasks due within next 7 days
- Shows countdown for each task: "in 3 days", "in 12 hours"
- Helps plan upcoming work

#### 16. Exit
Exit the application (all data is lost, reminder thread stops).

## Example Session

```
Welcome to Console Todo App!
Phase I - In-memory storage demo

=== Todo App ===
1. Add Task
2. View All Tasks
3. Update Task
4. Delete Task
5. Mark Complete/Incomplete
6. Exit

Enter choice: 1

--- Add Task ---
Title (required, 1-200 chars): Buy groceries
Description (optional, max 1000 chars): Milk, eggs, bread

✓ Task #1 created: Buy groceries

=== Todo App ===
...
Enter choice: 2

--- All Tasks ---
[ ] 1. Buy groceries (Pending)
   Milk, eggs, bread

Enter choice: 5

--- Mark Complete/Incomplete ---
Task ID: 1

✓ Task #1 marked as completed: Buy groceries

Enter choice: 2

--- All Tasks ---
[✓] 1. Buy groceries (Completed)
   Milk, eggs, bread
```

## Limitations (Phase I)

- **No Persistence**: Data stored in memory only - all tasks lost when application exits
- **Single User**: No user authentication or multi-user support
- **No Advanced Features** (deferred to future phases):
  - No due dates or reminders
  - No recurring tasks
  - No task dependencies or subtasks
  - No export/import functionality
  - No undo/redo operations

These limitations will be addressed in future phases:
- Phase II: Web application with database persistence and authentication
- Phase III: AI chatbot interface with MCP server integration
- Phase IV: Kubernetes deployment
- Phase V: Cloud-native with Kafka and Dapr

## Architecture

### Components

- **main.py**: CLI interface and user interaction flows
- **task_manager.py**: Business logic and in-memory data storage

### Data Model

```python
task = {
    "id": int,                    # Auto-increment unique ID
    "title": str,                 # 1-200 characters
    "description": str,           # Optional, max 1000 characters
    "completed": bool,            # Default False
    "priority": str,              # Priority level: "high", "medium", "low", "none" (default)
    "tags": list[str],            # 0-5 tags, alphanumeric, 1-20 chars each, lowercase
    "created_at": str,            # ISO format timestamp
    # Advanced fields
    "recurrence": dict | None,    # {"type": str, "interval": int, "days": list[str]} or None
    "due_date": str | None,       # ISO format datetime or None
    "reminder": dict | None,      # {"offset_minutes": int, "notified": bool} or None
    "parent_task_id": int | None  # Links to original recurring task or None
}
```

## Development

This application was built following spec-driven development principles:
1. **Specification** (`specs/001-console-todo-app/spec.md`): User stories and requirements
2. **Plan** (`specs/001-console-todo-app/plan.md`): Architecture and design decisions
3. **Tasks** (`specs/001-console-todo-app/tasks.md`): Implementation task breakdown
4. **Implementation**: Code generated by Claude Code

All code is 100% AI-generated following the hackathon's AI-native architecture principle.

## Project Structure

```
phase1/
├── src/
│   ├── __init__.py          # Package marker
│   ├── main.py              # CLI interface (915 lines) - Basic + Intermediate + Advanced
│   ├── task_manager.py      # Business logic (593 lines) - CRUD + Priorities/Tags/Search/Filter/Sort/Recurrence/DueDates/Reminders
│   └── reminder_thread.py   # Background thread (82 lines) - Reminder checking every 60 seconds
├── specs/
│   ├── 001-console-todo-app/     # Basic Level
│   │   ├── spec.md          # Feature specification (Basic)
│   │   ├── plan.md          # Implementation plan (Basic)
│   │   ├── tasks.md         # Task breakdown (T001-T058)
│   │   └── checklists/      # Quality validation
│   ├── 002-todo-intermediate/    # Intermediate Level
│   │   ├── spec.md          # Feature specification (Intermediate)
│   │   ├── plan.md          # Implementation plan (Intermediate)
│   │   ├── tasks.md         # Task breakdown (T059-T172)
│   │   └── checklists/      # Quality validation
│   ├── 003-todo-advanced/        # Advanced Level
│   │   ├── spec.md          # Feature specification (Advanced)
│   │   ├── plan.md          # Implementation plan (Advanced)
│   │   ├── tasks.md         # Task breakdown (T173-T420)
│   │   └── checklists/      # Quality validation
├── .gitignore               # Git ignore patterns
├── .python-version          # Python version (3.13)
├── pyproject.toml           # Project configuration
└── README.md                # This file
```

## Testing

Phase I uses manual validation against acceptance criteria. Automated testing will be introduced in Phase II.

### Manual Validation Checklist

- [x] Create task with title only
- [x] Create task with title + description
- [x] View empty list (friendly message)
- [x] View multiple tasks (newest first)
- [x] Mark task complete (shows [✓])
- [x] Mark task incomplete (shows [ ])
- [x] Update task title
- [x] Update task description
- [x] Delete task with confirmation
- [x] Delete task with "n" (cancelled)
- [x] All invalid inputs show error messages
- [x] Title validation (1-200 chars)
- [x] Description validation (max 1000 chars)
- [x] Task ID validation

## Success Criteria

- ✅ Users can create tasks in <10 seconds
- ✅ Users can view task list in <3 seconds
- ✅ Users can mark tasks complete in <5 seconds
- ✅ Users can update tasks in <15 seconds
- ✅ Users can delete tasks in <10 seconds
- ✅ Handles 100+ tasks without degradation
- ✅ All operations provide immediate feedback
- ✅ Full demo workflow completes in <90 seconds
- ✅ Zero crashes during normal operation
- ✅ Runs on WSL 2, Linux, and macOS

## License

Hackathon II - Evolution of Todo Project

## Next Steps

After validating Phase I:
1. Create demo video (<90 seconds)
2. Proceed to Phase II: Web Application with Persistence
   - Add PostgreSQL database (Neon)
   - Implement Better Auth with JWT
   - Build Next.js frontend
   - Deploy to cloud platform
