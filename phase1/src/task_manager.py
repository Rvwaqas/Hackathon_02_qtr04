"""
Task Manager Module - Business Logic and Data Storage

This module provides the TaskManager class which handles all CRUD operations
for task management with in-memory storage.
"""

from datetime import datetime, timedelta
from typing import Optional
import threading
import calendar


class TaskManager:
    """
    Manages tasks with in-memory storage.

    Provides methods for creating, reading, updating, and deleting tasks.
    Tasks are stored as dictionaries in a list, with auto-incrementing IDs.
    """

    def __init__(self) -> None:
        """Initialize empty task list and ID counter."""
        self.tasks: list[dict] = []
        self.next_id: int = 1
        self.lock: threading.Lock = threading.Lock()

    def _generate_id(self) -> int:
        """
        Generate unique task ID.

        Returns:
            int: Next available ID
        """
        current_id = self.next_id
        self.next_id += 1
        return current_id

    def get_task(self, task_id: int) -> Optional[dict]:
        """
        Find task by ID.

        Args:
            task_id: Task ID to find

        Returns:
            Task dictionary if found, None otherwise
        """
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_all_tasks(self) -> list[dict]:
        """
        Retrieve all tasks ordered by creation time (newest first).

        Returns:
            List of task dictionaries (empty list if none)
        """
        return sorted(self.tasks, key=lambda t: t["created_at"], reverse=True)

    def add_task(self, title: str, description: str = "") -> dict:
        """
        Create new task with unique ID.

        Args:
            title: Task title (1-200 chars, validated by caller)
            description: Optional description (max 1000 chars)

        Returns:
            Created task dictionary
        """
        task = {
            "id": self._generate_id(),
            "title": title.strip(),
            "description": description.strip(),
            "completed": False,
            "priority": "none",
            "tags": [],
            "recurrence": None,
            "due_date": None,
            "reminder": None,
            "parent_task_id": None,
            "created_at": datetime.now().isoformat()
        }
        self.tasks.append(task)
        return task

    def toggle_complete(self, task_id: int) -> dict:
        """
        Toggle task completion status.
        For recurring tasks, automatically creates next occurrence when completed.

        Args:
            task_id: Task ID to toggle

        Returns:
            Dictionary with {"current": task, "next": next_task or None}
        """
        task = self.get_task(task_id)
        if not task:
            return {"current": None, "next": None}

        task["completed"] = not task["completed"]

        # If completing a recurring task, create next occurrence
        next_task = None
        if task["completed"] and task.get("recurrence"):
            next_task = self.create_next_occurrence(task_id)

        return {"current": task, "next": next_task}

    def update_task(
        self,
        task_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[dict]:
        """
        Update task title and/or description.

        Args:
            task_id: Task ID to update
            title: New title (None = no change)
            description: New description (None = no change)

        Returns:
            Updated task dictionary if found, None otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return None

        if title is not None:
            task["title"] = title.strip()

        if description is not None:
            task["description"] = description.strip()

        return task

    def delete_task(self, task_id: int) -> bool:
        """
        Remove task from list.

        Args:
            task_id: Task ID to delete

        Returns:
            True if deleted, False if not found
        """
        task = self.get_task(task_id)
        if task:
            self.tasks.remove(task)
            return True
        return False

    def set_priority(self, task_id: int, priority: str) -> Optional[dict]:
        """
        Set task priority level.

        Args:
            task_id: Task ID to update
            priority: Priority level ("high", "medium", "low", or "none")

        Returns:
            Updated task dictionary if found and valid, None otherwise
        """
        valid_priorities = ["high", "medium", "low", "none"]
        if priority.lower() not in valid_priorities:
            return None

        task = self.get_task(task_id)
        if task:
            task["priority"] = priority.lower()
            return task
        return None

    def add_tags(self, task_id: int, new_tags: list[str]) -> Optional[dict]:
        """
        Add tags to task (max 5 total, alphanumeric only, 1-20 chars each).

        Args:
            task_id: Task ID to update
            new_tags: List of tag strings to add

        Returns:
            Updated task dictionary if successful, None otherwise
        """
        task = self.get_task(task_id)
        if not task:
            return None

        # Validate and normalize each tag
        for tag in new_tags:
            tag_stripped = tag.strip()

            # Skip empty tags
            if not tag_stripped:
                continue

            # Validate: alphanumeric only, 1-20 chars
            if not tag_stripped.isalnum() or len(tag_stripped) > 20 or len(tag_stripped) < 1:
                return None

            tag_lower = tag_stripped.lower()

            # Skip duplicates
            if tag_lower in task["tags"]:
                continue

            # Check total limit
            if len(task["tags"]) >= 5:
                return None

            task["tags"].append(tag_lower)

        return task

    def remove_tags(self, task_id: int, tags_to_remove: list[str]) -> Optional[dict]:
        """
        Remove tags from task.

        Args:
            task_id: Task ID to update
            tags_to_remove: List of tag strings to remove

        Returns:
            Updated task dictionary if found, None otherwise
        """
        task = self.get_task(task_id)
        if task:
            tags_lower = [tag.lower() for tag in tags_to_remove]
            task["tags"] = [t for t in task["tags"] if t not in tags_lower]
            return task
        return None

    def search_tasks(self, keyword: str) -> list[dict]:
        """
        Search tasks by keyword in title or description (case-insensitive).

        Args:
            keyword: Search keyword

        Returns:
            List of matching tasks (all tasks if keyword empty)
        """
        keyword_stripped = keyword.strip()
        if not keyword_stripped:
            return self.get_all_tasks()

        keyword_lower = keyword_stripped.lower()
        matches = []
        for task in self.tasks:
            if keyword_lower in task["title"].lower() or keyword_lower in task["description"].lower():
                matches.append(task)

        return sorted(matches, key=lambda t: t["created_at"], reverse=True)

    def filter_tasks(
        self,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tag: Optional[str] = None
    ) -> list[dict]:
        """
        Filter tasks by status, priority, and/or tag (AND logic).

        Args:
            status: Filter by status ("all", "pending", or "completed")
            priority: Filter by priority ("high", "medium", "low", or "none")
            tag: Filter by specific tag name

        Returns:
            List of filtered tasks
        """
        results = self.tasks[:]

        # Filter by status
        if status and status != "all":
            if status == "completed":
                results = [t for t in results if t["completed"]]
            elif status == "pending":
                results = [t for t in results if not t["completed"]]

        # Filter by priority
        if priority:
            results = [t for t in results if t["priority"] == priority.lower()]

        # Filter by tag
        if tag:
            results = [t for t in results if tag.lower() in t["tags"]]

        return sorted(results, key=lambda t: t["created_at"], reverse=True)

    def sort_tasks(self, sort_by: str, reverse: bool = False) -> list[dict]:
        """
        Sort tasks by specified criteria.

        Args:
            sort_by: Sort criteria ("created", "title", "priority", "status", or "due_date")
            reverse: True for descending, False for ascending

        Returns:
            Sorted list of tasks
        """
        priority_map = {"high": 3, "medium": 2, "low": 1, "none": 0}

        if sort_by == "created":
            key = lambda t: t["created_at"]
        elif sort_by == "title":
            key = lambda t: t["title"].lower()
        elif sort_by == "priority":
            key = lambda t: priority_map[t["priority"]]
            reverse = not reverse  # High first by default
        elif sort_by == "status":
            key = lambda t: t["completed"]
        elif sort_by == "due_date":
            # Sort by due date, None values go to end
            key = lambda t: t.get("due_date") or "9999-12-31"
        else:
            # Invalid criteria, return default order (newest first)
            return self.get_all_tasks()

        return sorted(self.tasks, key=key, reverse=reverse)

    def set_recurrence(
        self,
        task_id: int,
        rec_type: str,
        interval: int = 1,
        days: Optional[list[str]] = None
    ) -> Optional[dict]:
        """
        Set task recurrence pattern.

        Args:
            task_id: Task ID to update
            rec_type: Recurrence type ("daily", "weekly", "monthly", or "none")
            interval: Recurrence interval (default 1)
            days: List of weekday names for weekly recurrence (e.g., ["monday", "wednesday"])

        Returns:
            Updated task dictionary if found and valid, None otherwise
        """
        valid_types = ["daily", "weekly", "monthly", "none"]
        if rec_type.lower() not in valid_types:
            return None

        task = self.get_task(task_id)
        if not task:
            return None

        with self.lock:
            if rec_type.lower() == "none":
                task["recurrence"] = None
            else:
                task["recurrence"] = {
                    "type": rec_type.lower(),
                    "interval": interval,
                    "days": days or []
                }

        return task

    def calculate_next_due_date(self, task: dict) -> datetime:
        """
        Calculate next due date based on recurrence pattern.

        Args:
            task: Task dictionary with recurrence and due_date

        Returns:
            Next due date as datetime object
        """
        rec = task.get("recurrence")
        if not rec:
            return datetime.now()

        # Get current due date or use now
        if task.get("due_date"):
            if isinstance(task["due_date"], str):
                current_due = datetime.fromisoformat(task["due_date"])
            else:
                current_due = task["due_date"]
        else:
            current_due = datetime.now()

        interval = rec.get("interval", 1)

        if rec["type"] == "daily":
            return current_due + timedelta(days=interval)

        elif rec["type"] == "weekly":
            return current_due + timedelta(weeks=interval)

        elif rec["type"] == "monthly":
            # Handle month-end edge cases
            next_month = current_due.month + interval
            year = current_due.year + (next_month - 1) // 12
            month = (next_month - 1) % 12 + 1

            # Get last day of target month
            last_day = calendar.monthrange(year, month)[1]

            # Use minimum of current day or last day (handles day 31 → 28/29/30)
            day = min(current_due.day, last_day)

            return current_due.replace(year=year, month=month, day=day)

        return current_due

    def create_next_occurrence(self, task_id: int) -> Optional[dict]:
        """
        Create next occurrence of recurring task.

        Args:
            task_id: ID of recurring task to clone

        Returns:
            New task dictionary if successful, None otherwise
        """
        task = self.get_task(task_id)
        if not task or not task.get("recurrence"):
            return None

        # Calculate next due date
        next_due = self.calculate_next_due_date(task)

        with self.lock:
            # Clone task with new ID
            new_task = {
                "id": self._generate_id(),
                "title": task["title"],
                "description": task["description"],
                "completed": False,  # Reset completion status
                "priority": task["priority"],
                "tags": task["tags"].copy(),
                "recurrence": task["recurrence"].copy() if task["recurrence"] else None,
                "due_date": next_due.isoformat() if next_due else None,
                "reminder": task["reminder"].copy() if task.get("reminder") else None,
                "parent_task_id": task_id,  # Link to original
                "created_at": datetime.now().isoformat()
            }
            self.tasks.append(new_task)

        return new_task

    def set_due_date(self, task_id: int, due_date: datetime) -> Optional[dict]:
        """
        Set task due date.

        Args:
            task_id: Task ID to update
            due_date: Due date datetime object (must be in future)

        Returns:
            Updated task dictionary if successful, None otherwise
        """
        if due_date < datetime.now():
            return None  # Must be future date

        task = self.get_task(task_id)
        if not task:
            return None

        with self.lock:
            task["due_date"] = due_date.isoformat()

        return task

    def get_overdue_tasks(self) -> list[dict]:
        """
        Get tasks that are overdue.

        Returns:
            List of overdue tasks (due_date < now and not completed)
        """
        now = datetime.now()
        overdue = []

        with self.lock:
            for task in self.tasks:
                if task.get("due_date") and not task["completed"]:
                    due_date = datetime.fromisoformat(task["due_date"])
                    if now > due_date:
                        overdue.append(task)

        return sorted(overdue, key=lambda t: t["due_date"])

    def get_upcoming_tasks(self, days: int) -> list[dict]:
        """
        Get tasks due within specified number of days.

        Args:
            days: Number of days to look ahead

        Returns:
            List of tasks due within the specified timeframe
        """
        now = datetime.now()
        future = now + timedelta(days=days)
        upcoming = []

        with self.lock:
            for task in self.tasks:
                if task.get("due_date") and not task["completed"]:
                    due_date = datetime.fromisoformat(task["due_date"])
                    if now <= due_date <= future:
                        upcoming.append(task)

        return sorted(upcoming, key=lambda t: t["due_date"])

    def set_reminder(self, task_id: int, offset_minutes: int) -> Optional[dict]:
        """
        Set reminder for task (task must have due date).

        Args:
            task_id: Task ID to update
            offset_minutes: Minutes before due date to remind (15, 60, 1440, 10080)

        Returns:
            Updated task dictionary if successful, None otherwise
        """
        task = self.get_task(task_id)
        if not task or not task.get("due_date"):
            return None  # Task must have due date

        with self.lock:
            task["reminder"] = {
                "offset_minutes": offset_minutes,
                "notified": False
            }

        return task

    def get_pending_reminders(self) -> list[dict]:
        """
        Get tasks with reminders that haven't been notified yet.

        Returns:
            List of tasks with pending reminders
        """
        pending = []

        with self.lock:
            for task in self.tasks:
                if (task.get("reminder") and
                    not task["reminder"]["notified"] and
                    task.get("due_date") and
                    not task["completed"]):
                    pending.append(task)

        return pending

    def mark_reminder_notified(self, task_id: int) -> None:
        """
        Mark reminder as notified to prevent duplicates.

        Args:
            task_id: Task ID to update
        """
        task = self.get_task(task_id)
        if task and task.get("reminder"):
            with self.lock:
                task["reminder"]["notified"] = True

    def snooze_reminder(self, task_id: int, minutes: int) -> Optional[dict]:
        """
        Snooze reminder for specified minutes.

        Args:
            task_id: Task ID to update
            minutes: Minutes to snooze (typically 10)

        Returns:
            Updated task dictionary if successful, None otherwise
        """
        task = self.get_task(task_id)
        if not task or not task.get("reminder") or not task.get("due_date"):
            return None

        with self.lock:
            # Reset notified flag and update offset for snooze
            task["reminder"]["notified"] = False
            # Calculate new offset from now
            due_date = datetime.fromisoformat(task["due_date"])
            time_until_due = (due_date - datetime.now()).total_seconds() / 60
            task["reminder"]["offset_minutes"] = int(time_until_due - minutes)

        return task
