"""Dapr integration endpoints for sidecar communication.

Provides:
- GET /dapr/subscribe: Returns subscription list for Dapr Pub/Sub
- POST /events/task-events: Receives task lifecycle events
- POST /events/reminders: Receives reminder/recurring events

Phase V Part B: Publish-only pattern. Event receivers log events
but do not process them (consumers planned for Part C).
"""

import logging
from typing import Any, Dict, List

from fastapi import APIRouter, Request

logger = logging.getLogger("dapr")

router = APIRouter(tags=["dapr"])


@router.get("/dapr/subscribe")
async def dapr_subscribe() -> List[Dict[str, Any]]:
    """Return Dapr Pub/Sub subscription configuration.

    Dapr sidecar calls this endpoint on startup to discover
    which topics the application subscribes to.
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/events/task-events",
        },
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/events/reminders",
        },
    ]


@router.post("/events/task-events")
async def handle_task_event(request: Request) -> Dict[str, str]:
    """Receive task lifecycle events from Dapr Pub/Sub.

    Phase V Part B: Log-only consumer. Events are acknowledged
    but not processed. Full consumer logic planned for Part C.

    Returns {"status": "SUCCESS"} to acknowledge the event.
    Returning SUCCESS tells Dapr not to retry delivery.
    """
    body = await request.json()
    event_type = body.get("type", "unknown")
    event_id = body.get("id", "unknown")
    task_id = body.get("data", {}).get("task_id", "unknown")

    logger.info(
        f"Received task event: type={event_type}, "
        f"id={event_id}, task_id={task_id}"
    )

    return {"status": "SUCCESS"}


@router.post("/events/reminders")
async def handle_reminder_event(request: Request) -> Dict[str, str]:
    """Receive reminder and recurring task events from Dapr Pub/Sub.

    Phase V Part B: Log-only consumer. Events are acknowledged
    but not processed. Full consumer logic planned for Part C.

    Returns {"status": "SUCCESS"} to acknowledge the event.
    """
    body = await request.json()
    event_type = body.get("type", "unknown")
    event_id = body.get("id", "unknown")

    logger.info(
        f"Received reminder event: type={event_type}, id={event_id}"
    )

    return {"status": "SUCCESS"}
