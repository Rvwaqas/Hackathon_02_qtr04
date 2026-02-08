"""Event publishing service for Dapr Pub/Sub integration.

This module provides CloudEvents 1.0 compliant event publishing via Dapr sidecar.
Events are published asynchronously with graceful degradation - failures are logged
but do not block the main operation.

Phase V Part A: Code-level implementation only (no Dapr runtime deployment).
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

import httpx

# Configure logger
logger = logging.getLogger("event_publisher")


class EventPublisher:
    """Publishes events to Dapr Pub/Sub following CloudEvents 1.0 specification.

    This service provides fire-and-forget event publishing with graceful degradation.
    If Dapr sidecar is unavailable, events are logged but operations continue.

    Attributes:
        DAPR_HOST: Base URL for Dapr sidecar HTTP API
        PUBSUB_NAME: Name of the Dapr pub/sub component
        TOPIC_TASK_EVENTS: Topic for task lifecycle events
        TOPIC_REMINDERS: Topic for reminder and recurring triggers
    """

    DAPR_HOST = "http://localhost:3500"
    PUBSUB_NAME = "kafka-pubsub"

    # Topics
    TOPIC_TASK_EVENTS = "task-events"
    TOPIC_REMINDERS = "reminders"

    # Event types
    EVENT_TASK_CREATED = "com.todo.task.created"
    EVENT_TASK_UPDATED = "com.todo.task.updated"
    EVENT_TASK_COMPLETED = "com.todo.task.completed"
    EVENT_TASK_DELETED = "com.todo.task.deleted"
    EVENT_RECURRING_TRIGGERED = "com.todo.recurring.triggered"
    EVENT_REMINDER_DUE = "com.todo.reminder.due"

    @staticmethod
    def _create_cloud_event(
        event_type: str,
        source: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a CloudEvents 1.0 compliant event envelope.

        Args:
            event_type: The type of event (e.g., "com.todo.task.created")
            source: The source of the event (e.g., "/api/tasks")
            data: The event payload data

        Returns:
            Dict containing the complete CloudEvents envelope
        """
        return {
            "specversion": "1.0",
            "type": event_type,
            "source": source,
            "id": str(uuid.uuid4()),
            "time": datetime.utcnow().isoformat() + "Z",
            "datacontenttype": "application/json",
            "data": data
        }

    async def publish(
        self,
        topic: str,
        event_type: str,
        source: str,
        data: Dict[str, Any]
    ) -> bool:
        """Publish an event to Dapr Pub/Sub.

        This method is fire-and-forget with graceful degradation. If publishing
        fails (e.g., Dapr unavailable), it logs the error but does not raise
        an exception.

        Args:
            topic: The topic to publish to (e.g., "task-events")
            event_type: The CloudEvents type
            source: The CloudEvents source
            data: The event payload

        Returns:
            True if published successfully, False otherwise
        """
        event = self._create_cloud_event(event_type, source, data)
        url = f"{self.DAPR_HOST}/v1.0/publish/{self.PUBSUB_NAME}/{topic}"

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(
                    url,
                    json=event,
                    headers={"Content-Type": "application/cloudevents+json"}
                )

                if response.status_code == 204:
                    logger.info(
                        f"Event published successfully: type={event_type}, "
                        f"topic={topic}, id={event['id']}"
                    )
                    return True
                else:
                    logger.error(
                        f"Event publish failed: status={response.status_code}, "
                        f"type={event_type}, topic={topic}"
                    )
                    return False

        except httpx.ConnectError as e:
            logger.error(
                f"Dapr sidecar unavailable: {e}. "
                f"Event not published: type={event_type}, topic={topic}"
            )
            return False
        except httpx.TimeoutException as e:
            logger.error(
                f"Event publish timeout: {e}. "
                f"type={event_type}, topic={topic}"
            )
            return False
        except Exception as e:
            logger.error(
                f"Unexpected error publishing event: {e}. "
                f"type={event_type}, topic={topic}"
            )
            return False

    async def publish_task_event(
        self,
        event_type: str,
        task_id: int,
        user_id: int,
        task_data: Dict[str, Any]
    ) -> bool:
        """Publish a task lifecycle event.

        Helper method for publishing task-related events with consistent structure.

        Args:
            event_type: One of the EVENT_TASK_* constants
            task_id: The task ID
            user_id: The user ID who owns the task
            task_data: Full task data snapshot

        Returns:
            True if published successfully, False otherwise
        """
        data = {
            "task_id": task_id,
            "user_id": user_id,
            **task_data
        }

        return await self.publish(
            topic=self.TOPIC_TASK_EVENTS,
            event_type=event_type,
            source="/api/tasks",
            data=data
        )

    async def publish_reminder_event(
        self,
        task_id: int,
        user_id: int,
        title: str,
        due_date: Optional[datetime],
        reminder_time: datetime
    ) -> bool:
        """Publish a reminder due event.

        Helper method for publishing reminder trigger events.

        Args:
            task_id: The task ID
            user_id: The user ID
            title: The task title
            due_date: The task due date
            reminder_time: When the reminder should fire

        Returns:
            True if published successfully, False otherwise
        """
        data = {
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "due_date": due_date.isoformat() + "Z" if due_date else None,
            "reminder_time": reminder_time.isoformat() + "Z"
        }

        return await self.publish(
            topic=self.TOPIC_REMINDERS,
            event_type=self.EVENT_REMINDER_DUE,
            source="/services/scheduler",
            data=data
        )

    async def publish_recurring_triggered(
        self,
        parent_task_id: int,
        new_task_id: int,
        user_id: int,
        title: str,
        recurrence_type: str,
        previous_due_date: Optional[datetime],
        next_due_date: Optional[datetime]
    ) -> bool:
        """Publish a recurring task triggered event.

        Called when a recurring task is completed and creates its next occurrence.

        Args:
            parent_task_id: The completed task ID
            new_task_id: The newly created task ID
            user_id: The user ID
            title: The task title
            recurrence_type: Type of recurrence (daily/weekly/monthly)
            previous_due_date: Due date of completed task
            next_due_date: Due date of new task

        Returns:
            True if published successfully, False otherwise
        """
        data = {
            "parent_task_id": parent_task_id,
            "new_task_id": new_task_id,
            "user_id": user_id,
            "title": title,
            "recurrence_type": recurrence_type,
            "previous_due_date": previous_due_date.isoformat() + "Z" if previous_due_date else None,
            "next_due_date": next_due_date.isoformat() + "Z" if next_due_date else None
        }

        return await self.publish(
            topic=self.TOPIC_REMINDERS,
            event_type=self.EVENT_RECURRING_TRIGGERED,
            source="/api/tasks",
            data=data
        )


# Singleton instance for easy import
event_publisher = EventPublisher()
