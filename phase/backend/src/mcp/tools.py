"""MCP tools for todo task management - wrapping existing TaskService."""

from typing import Optional, Dict, Any
from uuid import UUID

from sqlmodel import Session

from src.models.task import Task
from src.services.task import TaskService
from src.schemas import TaskCreate, TaskUpdate


class TodoToolsHandler:
    """MCP tool handler that wraps TaskService for agent use."""

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
        **kwargs
    ) -> Dict[str, Any]:
        """Create a new task for the authenticated user.

        Args:
            title: Task title (required)
            description: Task description (optional)
            priority: Task priority: 'low', 'medium', 'high' (optional)
            due_date: Due date in ISO 8601 format (optional)

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
                tags=kwargs.get("tags", []),
            )

            task = await self.task_service.create_task(
                self.session, self.user_id, task_data
            )

            return {
                "success": True,
                "task_id": str(task.id),
                "message": f"Task '{title}' added! [COMPLETED]"
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
        **kwargs
    ) -> Dict[str, Any]:
        """Retrieve tasks for the authenticated user with optional filtering.

        Args:
            status: Filter by status: 'pending', 'completed', 'all' (optional)
            priority: Filter by priority: 'low', 'medium', 'high', 'all' (optional)

        Returns:
            Dict with success status, task list, and count
        """
        try:
            # Get tasks using existing service
            tasks = await self.task_service.get_tasks(
                self.session,
                self.user_id,
                status=status if status != "all" else None,
                priority=priority if priority != "all" else None,
            )

            # Format tasks for agent response
            formatted_tasks = [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "status": "completed" if task.completed else "pending",
                    "priority": task.priority,
                }
                for task in tasks
            ]

            if not formatted_tasks:
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

            # Mark as complete
            update_data = TaskUpdate(completed=True)
            completed_task = await self.task_service.update_task(
                self.session, task_id_int, self.user_id, update_data
            )

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
        **kwargs
    ) -> Dict[str, Any]:
        """Modify task properties for the authenticated user.

        Args:
            task_id: ID of task to update
            title: New title (optional)
            description: New description (optional)
            priority: New priority (optional)
            status: New status: 'pending' or 'completed' (optional)

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

            # Build update object
            update_fields = {}
            if title:
                update_fields["title"] = title.strip()
            if description is not None:
                update_fields["description"] = description.strip() if description else None
            if priority:
                update_fields["priority"] = priority
            if status:
                update_fields["completed"] = (status == "completed")

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

            return {
                "success": True,
                "task_id": str(task_id),
                "message": f"Task {task_id} updated! [UPDATED]"
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
