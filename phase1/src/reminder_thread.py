"""
Reminder Thread Module - Background Reminder Checking

This module provides the ReminderThread class which runs in the background
to check for pending reminders and queue notifications for the main CLI thread.
"""

import threading
import time
from datetime import datetime, timedelta
from queue import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from task_manager import TaskManager


class ReminderThread(threading.Thread):
    """
    Background thread that checks for pending reminders every 60 seconds.

    This thread runs as a daemon and automatically stops when the main app exits.
    Uses a Queue for thread-safe communication with the main CLI thread.
    """

    def __init__(self, task_manager: "TaskManager", notification_queue: Queue):
        """
        Initialize reminder thread.

        Args:
            task_manager: TaskManager instance to check for reminders
            notification_queue: Queue to send notification tasks to main thread
        """
        super().__init__(daemon=True)
        self.task_manager = task_manager
        self.notification_queue = notification_queue
        self.running = True

    def run(self) -> None:
        """
        Main thread loop - checks reminders every 60 seconds.
        Runs continuously until stop() is called or app exits.
        """
        while self.running:
            self.check_reminders()
            time.sleep(60)  # Check every 60 seconds

    def check_reminders(self) -> None:
        """
        Check for reminders that need to be triggered.
        Called every 60 seconds by the run() loop.
        """
        now = datetime.now()
        pending = self.task_manager.get_pending_reminders()

        for task in pending:
            try:
                # Parse due date
                due_date = datetime.fromisoformat(task["due_date"])

                # Calculate reminder trigger time
                offset_minutes = task["reminder"]["offset_minutes"]
                reminder_time = due_date - timedelta(minutes=offset_minutes)

                # Check if reminder time has been reached
                if now >= reminder_time:
                    # Queue notification for main thread
                    self.notification_queue.put(task)

                    # Mark as notified to prevent duplicates
                    self.task_manager.mark_reminder_notified(task["id"])

            except (ValueError, KeyError, TypeError):
                # Skip tasks with invalid date formats or missing fields
                continue

    def stop(self) -> None:
        """
        Gracefully stop the reminder thread.
        Sets running flag to False to exit the run() loop.
        """
        self.running = False
