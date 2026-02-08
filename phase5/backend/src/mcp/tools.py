"""MCP tools for todo task management - wrapping existing TaskService.

Phase V Part A: Enhanced with priority, tags, search, filter, sort, recurrence,
due dates, and reminder support.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from sqlmodel import Session

from src.models.task import Task
from src.services.task import TaskService
from src.schemas import TaskCreate, TaskUpdate


class TodoToolsHandler:
    """MCP tool handler that wraps TaskService for agent use.

    Phase V Part A enhancements:
    - add_task: supports tags, recurrence, reminder_offset_minutes
    - list_tasks: supports tag filter, search, sort, order
    - complete_task: handles recurring tasks (creates next occurrence)
    - update_task: supports tags, recurrence, reminder, due_date
    """

    def __init__(self, session: Session, user_id: str):
        """Initialize with database session and authenticated user_id.

        Args:
            session: SQLModel session for database operations
            user_id: Authenticated user ID (from JWT)
        """
        self.session = session
        # Convert user_id to int since database expects integer
        self.user_id = int(user_id) if isinstance(user_id, str) else user_id
        self.task_service = TaskService()

    async def add_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        recurrence: Optional[Dict[str, Any]] = None,
        reminder_offset_minutes: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new task for the authenticated user.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority: 'low', 'medium', 'high', 'none' (optional)
            due_date: Due date in ISO 8601 format (optional)
            tags: List of category tags (optional)
            recurrence: Recurrence config with type, interval, end_date (optional)
            reminder_offset_minutes: Minutes before due_date to remind (optional)

        Returns:
            Dict with success status, task ID, and confirmation message
        """
        try:
            if not title or not title.strip():
                return {
                    "success": False,
                    "error": "invalid_input",
                    "message": "Title is required"
                }

            # Create task using existing service
            task_data = TaskCreate(
                title=title.strip(),
                description=description.strip() if description else None,
                priority=priority or "medium",
                due_date=due_date,
                tags=tags or kwargs.get("tags", []),
                recurrence=recurrence,
                reminder_offset_minutes=reminder_offset_minutes,
            )

            task = await self.task_service.create_task(
                self.session, self.user_id, task_data
            )

            # Build detailed confirmation message
            details = []
            if task.priority and task.priority != "none":
                details.append(f"priority {task.priority.upper()}")
            if task.tags:
                details.append(f"tagged [{', '.join(task.tags)}]")
            if task.due_date:
                details.append(f"due {task.due_date.strftime('%Y-%m-%d')}")
            if task.recurrence:
                rec_type = task.recurrence.get("type", "")
                details.append(f"repeats {rec_type}")
            if task.reminder_offset_minutes:
                details.append(f"reminder {task.reminder_offset_minutes}min before")

            detail_str = f" with {', '.join(details)}" if details else ""

            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{title}' added{detail_str}! [CREATED]"
            }

        except Exception as e:
            return {
                "success": False,
                "error": "creation_error",
                "message": f"Failed to create task: {str(e)}"
            }

    async def list_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None,
        search: Optional[str] = None,
        sort: Optional[str] = None,
        order: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Retrieve tasks for the authenticated user with optional filtering.

        Args:
            status: Filter by status: 'pending', 'completed', 'all' (optional)
            priority: Filter by priority: 'low', 'medium', 'high', 'all' (optional)
            tag: Filter by tag name (optional)
            search: Search keyword in title/description (optional)
            sort: Sort field: 'created_at', 'due_date', 'priority', 'title' (optional)
            order: Sort order: 'asc' or 'desc' (optional, default 'desc')

        Returns:
            Dict with success status, task list, and count
        """
        try:
            # Get tasks using existing service with all filter params
            tasks = await self.task_service.get_tasks(
                self.session,
                self.user_id,
                status=status if status != "all" else None,
                priority=priority if priority != "all" else None,
                tag=tag,
                search=search,
                sort=sort or "created_at",
                order=order or "desc",
            )

            # Format tasks for agent response with all Phase V fields
            formatted_tasks = []
            for task in tasks:
                task_dict = {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": "completed" if task.completed else "pending",
                    "priority": task.priority or "none",
                    "tags": task.tags or [],
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "recurrence": task.recurrence,
                    "reminder_offset_minutes": task.reminder_offset_minutes,
                }
                formatted_tasks.append(task_dict)

            if not formatted_tasks:
                # Build contextual empty message
                filters_applied = []
                if status and status != "all":
                    filters_applied.append(f"status={status}")
                if priority and priority != "all":
                    filters_applied.append(f"priority={priority}")
                if tag:
                    filters_applied.append(f"tag={tag}")
                if search:
                    filters_applied.append(f"search='{search}'")

                if filters_applied:
                    filter_str = ", ".join(filters_applied)
                    return {
                        "success": True,
                        "tasks": [],
                        "count": 0,
                        "message": f"No tasks found matching filters: {filter_str}"
                    }
                return {
                    "success": True,
                    "tasks": [],
                    "count": 0,
                    "message": "You don't have any tasks yet. You can add one by telling me what you need to do."
                }

            return {
                "success": True,
                "tasks": formatted_tasks,
                "count": len(formatted_tasks),
                "message": f"Found {len(formatted_tasks)} task(s)"
            }

        except Exception as e:
            return {
                "success": False,
                "error": "retrieval_error",
                "message": f"Failed to retrieve tasks: {str(e)}"
            }

    async def complete_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Mark a task as complete for the authenticated user.

        For recurring tasks, this automatically creates the next occurrence.

        Args:
            task_id: ID of task to complete

        Returns:
            Dict with success status and confirmation message
        """
        try:
            # Convert string ID to int if needed
            task_id_int = int(task_id)

            # Get task to verify ownership
            task = await self.task_service.get_task(
                self.session, task_id_int, self.user_id
            )

            if not task:
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"I couldn't find task {task_id} in your pending tasks."
                }

            if task.completed:
                return {
                    "success": False,
                    "error": "already_completed",
                    "message": f"Task {task_id} is already completed."
                }

            # Use toggle_complete which handles recurring tasks
            result = await self.task_service.toggle_complete(
                self.session, task_id_int, self.user_id
            )

            if not result:
                return {
                    "success": False,
                    "error": "update_error",
                    "message": f"Failed to complete task {task_id}"
                }

            completed_task, next_task = result

            # Build response message
            if next_task:
                # Recurring task - next occurrence created
                next_due = ""
                if next_task.due_date:
                    next_due = f" (next due: {next_task.due_date.strftime('%Y-%m-%d')})"
                return {
                    "success": True,
                    "task_id": str(task_id),
                    "next_task_id": str(next_task.id),
                    "message": f"Task {task_id} marked as complete! [DONE] Next occurrence #{next_task.id} created{next_due}."
                }
            else:
                return {
                    "success": True,
                    "task_id": str(task_id),
                    "message": f"Task {task_id} marked as complete! [DONE]"
                }

        except ValueError:
            return {
                "success": False,
                "error": "invalid_id",
                "message": f"Invalid task ID: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "update_error",
                "message": f"Failed to complete task: {str(e)}"
            }

    async def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        due_date: Optional[str] = None,
        tags: Optional[List[str]] = None,
        recurrence: Optional[Dict[str, Any]] = None,
        reminder_offset_minutes: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Modify task properties for the authenticated user.

        Args:
            task_id: ID of task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status: 'pending' or 'completed' (optional)
            due_date: New due date in ISO 8601 format (optional)
            tags: New tags list - replaces existing (optional)
            recurrence: New recurrence config or null to stop (optional)
            reminder_offset_minutes: New reminder offset (optional)

        Returns:
            Dict with success status and confirmation message
        """
        try:
            task_id_int = int(task_id)

            # Get task to verify ownership
            task = await self.task_service.get_task(
                self.session, task_id_int, self.user_id
            )

            if not task:
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"I couldn't find task {task_id}."
                }

            # Build update object with all Phase V fields
            update_fields = {}
            changes = []

            if title:
                update_fields["title"] = title.strip()
                changes.append("title")
            if description is not None:
                update_fields["description"] = description.strip() if description else None
                changes.append("description")
            if priority:
                update_fields["priority"] = priority
                changes.append(f"priority→{priority}")
            if status:
                update_fields["completed"] = (status == "completed")
                changes.append(f"status→{status}")
            if due_date is not None:
                update_fields["due_date"] = due_date
                changes.append("due_date")
            if tags is not None:
                update_fields["tags"] = tags
                changes.append(f"tags→[{', '.join(tags)}]" if tags else "tags cleared")
            if recurrence is not None:
                update_fields["recurrence"] = recurrence
                if recurrence:
                    rec_type = recurrence.get("type", "")
                    changes.append(f"recurrence→{rec_type}")
                else:
                    changes.append("recurrence stopped")
            if reminder_offset_minutes is not None:
                update_fields["reminder_offset_minutes"] = reminder_offset_minutes
                changes.append(f"reminder→{reminder_offset_minutes}min")

            if not update_fields:
                return {
                    "success": False,
                    "error": "no_updates",
                    "message": "No fields to update. Please specify what you'd like to change."
                }

            update_data = TaskUpdate(**update_fields)
            updated_task = await self.task_service.update_task(
                self.session, task_id_int, self.user_id, update_data
            )

            changes_str = ", ".join(changes)
            return {
                "success": True,
                "task_id": str(task_id),
                "message": f"Task {task_id} updated: {changes_str}! [UPDATED]"
            }

        except ValueError:
            return {
                "success": False,
                "error": "invalid_id",
                "message": f"Invalid task ID: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "update_error",
                "message": f"Failed to update task: {str(e)}"
            }

    async def delete_task(self, task_id: str, **kwargs) -> Dict[str, Any]:
        """Remove a task for the authenticated user.

        Args:
            task_id: ID of task to delete

        Returns:
            Dict with success status and confirmation message
        """
        try:
            task_id_int = int(task_id)

            # Get task to verify ownership
            task = await self.task_service.get_task(
                self.session, task_id_int, self.user_id
            )

            if not task:
                return {
                    "success": False,
                    "error": "not_found",
                    "message": f"I couldn't find task {task_id}."
                }

            # Delete task
            await self.task_service.delete_task(self.session, task_id_int, self.user_id)

            return {
                "success": True,
                "task_id": str(task_id),
                "message": f"Task {task_id} deleted. [REMOVED]"
            }

        except ValueError:
            return {
                "success": False,
                "error": "invalid_id",
                "message": f"Invalid task ID: {task_id}"
            }
        except Exception as e:
            return {
                "success": False,
                "error": "delete_error",
                "message": f"Failed to delete task: {str(e)}"
            }
