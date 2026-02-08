# Skill: Kafka Event Architecture

## Purpose
Design and implement event-driven systems with Kafka (Redpanda Cloud or Strimzi). Define topics, event schemas, publishing/consuming patterns via Dapr Pub/Sub abstraction.

## Tech Stack
- **Kafka**: Event streaming platform
- **Redpanda Cloud**: Serverless Kafka-compatible (recommended for free tier)
- **Strimzi**: Kubernetes operator for self-hosted Kafka
- **Dapr Pub/Sub**: Abstraction layer for publishing/consuming
- **CloudEvents**: Standard event format

## Rule #1: ALL Kafka Access via Dapr

```
❌ WRONG - Direct Kafka Client
──────────────────────────────────────
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka:9092')
producer.send('task-events', value=event)

✅ CORRECT - Via Dapr Pub/Sub
──────────────────────────────────────
import httpx
await httpx.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event
)
```

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        EVENT-DRIVEN ARCHITECTURE                         │
│                                                                          │
│  PRODUCERS                      KAFKA TOPICS                CONSUMERS    │
│  ─────────                      ────────────                ─────────    │
│                                                                          │
│  ┌─────────────┐               ┌─────────────┐         ┌──────────────┐ │
│  │   Backend   │──publish──────│ task-events │─────────│  Recurring   │ │
│  │   Service   │               │ (3 parts)   │         │   Service    │ │
│  └─────────────┘               └─────────────┘         └──────────────┘ │
│        │                                                                 │
│        │                       ┌─────────────┐         ┌──────────────┐ │
│        └───publish─────────────│  reminders  │─────────│ Notification │ │
│                                │ (3 parts)   │         │   Service    │ │
│                                └─────────────┘         └──────────────┘ │
│                                                                          │
│                                ┌─────────────┐         ┌──────────────┐ │
│                                │task-updates │─────────│  WebSocket   │ │
│                                │ (3 parts)   │         │   Gateway    │ │
│                                └─────────────┘         └──────────────┘ │
│                                                                          │
│  ════════════════════════════════════════════════════════════════════   │
│                          ALL VIA DAPR SIDECAR                            │
│                         (localhost:3500/publish)                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Part 1: Topic Definitions

### Standard Topics for Todo Application

| Topic | Purpose | Partition Key | Retention |
|-------|---------|---------------|-----------|
| `task-events` | Task lifecycle (CRUD) | `user_id` | 7 days |
| `reminders` | Reminder triggers | `user_id` | 3 days |
| `task-updates` | Real-time UI updates | `user_id` | 1 day |

### Topic Configuration

```yaml
# Topics Configuration Reference
# [Task]: Define Kafka topics for todo application

topics:
  task-events:
    partitions: 3
    replication_factor: 1  # Use 3 in production
    retention_ms: 604800000  # 7 days
    cleanup_policy: delete
    key: user_id  # Ensures ordering per user

  reminders:
    partitions: 3
    replication_factor: 1
    retention_ms: 259200000  # 3 days
    cleanup_policy: delete
    key: user_id

  task-updates:
    partitions: 3
    replication_factor: 1
    retention_ms: 86400000  # 1 day
    cleanup_policy: delete
    key: user_id
```

### Partitioning Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                    PARTITIONING BY user_id                   │
│                                                              │
│  User A's events ────────────────────────► Partition 0       │
│  User B's events ────────────────────────► Partition 1       │
│  User C's events ────────────────────────► Partition 2       │
│                                                              │
│  Benefits:                                                   │
│  ✅ Events for same user always in order                     │
│  ✅ Parallel processing across users                         │
│  ✅ Consumer can scale to partition count                    │
└─────────────────────────────────────────────────────────────┘
```

## Part 2: Event Schemas (CloudEvents Format)

### 2.1 Task Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TaskEvent",
  "description": "CloudEvents-compliant task lifecycle event",
  "type": "object",
  "required": ["specversion", "type", "source", "id", "time", "data"],
  "properties": {
    "specversion": {
      "type": "string",
      "const": "1.0"
    },
    "type": {
      "type": "string",
      "enum": [
        "com.taskmanager.task.created",
        "com.taskmanager.task.updated",
        "com.taskmanager.task.completed",
        "com.taskmanager.task.deleted"
      ]
    },
    "source": {
      "type": "string",
      "pattern": "^/tasks/[a-z-]+$",
      "example": "/tasks/backend-service"
    },
    "id": {
      "type": "string",
      "format": "uuid"
    },
    "time": {
      "type": "string",
      "format": "date-time"
    },
    "datacontenttype": {
      "type": "string",
      "const": "application/json"
    },
    "data": {
      "type": "object",
      "required": ["task_id", "user_id"],
      "properties": {
        "task_id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "description": { "type": "string" },
        "priority": { "enum": ["high", "medium", "low"] },
        "tags": { "type": "array", "items": { "type": "string" } },
        "completed": { "type": "boolean" },
        "due_date": { "type": "string", "format": "date-time" },
        "changes": {
          "type": "object",
          "description": "For update events, contains changed fields"
        }
      }
    }
  }
}
```

### 2.2 Reminder Event Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "ReminderEvent",
  "description": "Reminder notification event",
  "type": "object",
  "required": ["specversion", "type", "source", "id", "time", "data"],
  "properties": {
    "specversion": { "const": "1.0" },
    "type": {
      "enum": [
        "com.taskmanager.reminder.scheduled",
        "com.taskmanager.reminder.triggered",
        "com.taskmanager.reminder.cancelled"
      ]
    },
    "source": { "type": "string" },
    "id": { "type": "string", "format": "uuid" },
    "time": { "type": "string", "format": "date-time" },
    "data": {
      "type": "object",
      "required": ["task_id", "user_id", "remind_at"],
      "properties": {
        "task_id": { "type": "integer" },
        "user_id": { "type": "string" },
        "title": { "type": "string" },
        "due_at": { "type": "string", "format": "date-time" },
        "remind_at": { "type": "string", "format": "date-time" },
        "remind_before_minutes": { "type": "integer" }
      }
    }
  }
}
```

### 2.3 Task Update Event Schema (Real-time)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "TaskUpdateEvent",
  "description": "Real-time task update for UI sync",
  "type": "object",
  "properties": {
    "specversion": { "const": "1.0" },
    "type": {
      "enum": [
        "com.taskmanager.ui.task_list_changed",
        "com.taskmanager.ui.task_status_changed"
      ]
    },
    "data": {
      "properties": {
        "user_id": { "type": "string" },
        "action": { "enum": ["refresh", "add", "update", "remove"] },
        "task_id": { "type": "integer" },
        "task_snapshot": { "type": "object" }
      }
    }
  }
}
```

## Part 3: Publishing Events via Dapr

### 3.1 Event Publisher Module

```python
"""
backend/services/kafka_publisher.py
[Task]: Publish events to Kafka via Dapr Pub/Sub
[Rule]: NEVER use kafka-python, aiokafka, or confluent-kafka directly
"""

import httpx
import json
import uuid
from datetime import datetime
from typing import Literal, Optional, Any
from pydantic import BaseModel

# Dapr configuration
DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

# Topic names
TOPIC_TASK_EVENTS = "task-events"
TOPIC_REMINDERS = "reminders"
TOPIC_TASK_UPDATES = "task-updates"


class CloudEvent(BaseModel):
    """CloudEvents 1.0 compliant event structure"""
    specversion: str = "1.0"
    type: str
    source: str
    id: str
    time: str
    datacontenttype: str = "application/json"
    data: dict


async def publish_to_kafka(
    topic: str,
    event_type: str,
    data: dict,
    source: str = "/tasks/backend-service",
    partition_key: Optional[str] = None
) -> bool:
    """
    Publish event to Kafka topic via Dapr Pub/Sub.

    [Spec]: CloudEvents format with partition key for ordering
    [Rule]: All publishing through localhost:3500

    Args:
        topic: Kafka topic (task-events, reminders, task-updates)
        event_type: CloudEvents type (com.taskmanager.task.created, etc.)
        data: Event payload
        source: Event source identifier
        partition_key: Key for partitioning (usually user_id)

    Returns:
        True if published successfully
    """
    event = CloudEvent(
        type=event_type,
        source=source,
        id=str(uuid.uuid4()),
        time=datetime.utcnow().isoformat() + "Z",
        data=data
    )

    headers = {
        "Content-Type": "application/cloudevents+json"
    }

    # Add partition key for ordering (Dapr metadata)
    if partition_key:
        headers["metadata.partitionKey"] = partition_key

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event.model_dump(),
                headers=headers,
                timeout=10.0
            )
            response.raise_for_status()
            return True

    except httpx.HTTPStatusError as e:
        print(f"Kafka publish failed: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"Kafka publish error: {e}")
        return False


# ═══════════════════════════════════════════════════════════════
# TASK EVENTS
# ═══════════════════════════════════════════════════════════════

async def publish_task_created(
    task_id: int,
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium",
    tags: list = None,
    due_date: Optional[datetime] = None
) -> bool:
    """Publish task.created event"""
    return await publish_to_kafka(
        topic=TOPIC_TASK_EVENTS,
        event_type="com.taskmanager.task.created",
        data={
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "description": description,
            "priority": priority,
            "tags": tags or [],
            "due_date": due_date.isoformat() if due_date else None,
            "completed": False
        },
        partition_key=user_id  # Ensures ordering per user
    )


async def publish_task_updated(
    task_id: int,
    user_id: str,
    changes: dict
) -> bool:
    """Publish task.updated event with changed fields"""
    return await publish_to_kafka(
        topic=TOPIC_TASK_EVENTS,
        event_type="com.taskmanager.task.updated",
        data={
            "task_id": task_id,
            "user_id": user_id,
            "changes": changes
        },
        partition_key=user_id
    )


async def publish_task_completed(
    task_id: int,
    user_id: str,
    is_recurring: bool = False
) -> bool:
    """Publish task.completed event"""
    return await publish_to_kafka(
        topic=TOPIC_TASK_EVENTS,
        event_type="com.taskmanager.task.completed",
        data={
            "task_id": task_id,
            "user_id": user_id,
            "is_recurring": is_recurring
        },
        partition_key=user_id
    )


async def publish_task_deleted(task_id: int, user_id: str) -> bool:
    """Publish task.deleted event"""
    return await publish_to_kafka(
        topic=TOPIC_TASK_EVENTS,
        event_type="com.taskmanager.task.deleted",
        data={"task_id": task_id, "user_id": user_id},
        partition_key=user_id
    )


# ═══════════════════════════════════════════════════════════════
# REMINDER EVENTS
# ═══════════════════════════════════════════════════════════════

async def publish_reminder_scheduled(
    task_id: int,
    user_id: str,
    title: str,
    due_at: datetime,
    remind_at: datetime
) -> bool:
    """Publish reminder.scheduled event"""
    return await publish_to_kafka(
        topic=TOPIC_REMINDERS,
        event_type="com.taskmanager.reminder.scheduled",
        data={
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "due_at": due_at.isoformat(),
            "remind_at": remind_at.isoformat()
        },
        partition_key=user_id
    )


async def publish_reminder_triggered(
    task_id: int,
    user_id: str,
    title: str
) -> bool:
    """Publish reminder.triggered event (for notification service)"""
    return await publish_to_kafka(
        topic=TOPIC_REMINDERS,
        event_type="com.taskmanager.reminder.triggered",
        data={
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "triggered_at": datetime.utcnow().isoformat()
        },
        partition_key=user_id
    )


# ═══════════════════════════════════════════════════════════════
# REAL-TIME UI UPDATE EVENTS
# ═══════════════════════════════════════════════════════════════

async def publish_ui_update(
    user_id: str,
    action: Literal["refresh", "add", "update", "remove"],
    task_id: Optional[int] = None,
    task_snapshot: Optional[dict] = None
) -> bool:
    """Publish real-time update for WebSocket/SSE consumers"""
    return await publish_to_kafka(
        topic=TOPIC_TASK_UPDATES,
        event_type="com.taskmanager.ui.task_list_changed",
        data={
            "user_id": user_id,
            "action": action,
            "task_id": task_id,
            "task_snapshot": task_snapshot
        },
        partition_key=user_id
    )
```

### 3.2 Integration with MCP Tools

```python
"""
Integrate Kafka publishing with MCP tools
[Task]: Event-driven task management
"""

from services.kafka_publisher import (
    publish_task_created,
    publish_task_completed,
    publish_task_deleted,
    publish_ui_update
)

@mcp.tool()
async def add_task(
    user_id: str,
    title: str,
    description: str = "",
    priority: str = "medium"
) -> str:
    """Create task and publish events"""

    # 1. Create in database
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority
    )
    session.add(task)
    await session.commit()

    # 2. Publish task.created event (for recurring service, analytics, etc.)
    await publish_task_created(
        task_id=task.id,
        user_id=user_id,
        title=title,
        description=description,
        priority=priority
    )

    # 3. Publish UI update (for real-time refresh)
    await publish_ui_update(
        user_id=user_id,
        action="add",
        task_id=task.id,
        task_snapshot=task.to_dict()
    )

    return json.dumps({"task_id": task.id, "status": "created"})
```

## Part 4: Consumer Patterns

### 4.1 Recurring Task Service (Consumer)

```python
"""
services/recurring_task_service.py
[Task]: Consume task.completed events and create next occurrences
[Pattern]: Event-driven saga
"""

from fastapi import FastAPI, Request
from datetime import datetime, timedelta

app = FastAPI()

@app.post("/task-events")
async def handle_task_event(request: Request):
    """
    Dapr subscription callback for task-events topic.

    [Spec]: Listen for task.completed, create next occurrence if recurring
    """
    cloud_event = await request.json()
    event_type = cloud_event.get("type")
    data = cloud_event.get("data", {})

    if event_type == "com.taskmanager.task.completed":
        task_id = data.get("task_id")
        user_id = data.get("user_id")
        is_recurring = data.get("is_recurring", False)

        if is_recurring:
            # Fetch task details and create next occurrence
            await create_next_occurrence(task_id, user_id)
            print(f"✅ Created next occurrence for recurring task {task_id}")

    return {"status": "SUCCESS"}


@app.get("/dapr/subscribe")
async def subscribe():
    """Tell Dapr which topics to subscribe to"""
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/task-events"
        }
    ]


async def create_next_occurrence(task_id: int, user_id: str):
    """
    Create next occurrence based on recurrence rule.

    [Spec]: Support daily, weekly, monthly intervals
    """
    # Fetch original task
    task = await get_task(task_id)

    if not task or not task.recurring_interval:
        return

    # Calculate next due date
    intervals = {
        "daily": timedelta(days=1),
        "weekly": timedelta(weeks=1),
        "monthly": timedelta(days=30)
    }

    next_due = task.due_date + intervals.get(task.recurring_interval, timedelta(days=1))

    # Create new task via internal API
    new_task = Task(
        user_id=user_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        due_date=next_due,
        recurring_interval=task.recurring_interval,
        parent_task_id=task_id
    )

    session.add(new_task)
    await session.commit()

    # Publish event for the new task
    await publish_task_created(
        task_id=new_task.id,
        user_id=user_id,
        title=new_task.title,
        due_date=next_due
    )
```

### 4.2 Notification Service (Consumer)

```python
"""
services/notification_service.py
[Task]: Consume reminder events and send notifications
"""

from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/reminders")
async def handle_reminder(request: Request):
    """
    Dapr subscription callback for reminders topic.

    [Spec]: Send push/email notification when reminder triggers
    """
    cloud_event = await request.json()
    event_type = cloud_event.get("type")
    data = cloud_event.get("data", {})

    if event_type == "com.taskmanager.reminder.triggered":
        user_id = data.get("user_id")
        title = data.get("title")
        task_id = data.get("task_id")

        # Send notification (implement your notification logic)
        await send_notification(
            user_id=user_id,
            title=f"Reminder: {title}",
            body=f"Task #{task_id} is due soon!",
            notification_type="reminder"
        )

        print(f"📧 Sent reminder notification to {user_id}")

    return {"status": "SUCCESS"}


@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/reminders"
        }
    ]


async def send_notification(user_id: str, title: str, body: str, notification_type: str):
    """
    Send notification via configured channel.

    [Spec]: Support email, push, in-app notifications
    """
    # Get user preferences
    user = await get_user(user_id)

    if user.email_notifications:
        await send_email(user.email, title, body)

    if user.push_notifications:
        await send_push(user.device_tokens, title, body)

    # Always log to in-app notifications
    await create_in_app_notification(user_id, title, body, notification_type)
```

## Part 5: Platform Setup

### Option A: Redpanda Cloud (Recommended - Free Tier)

```bash
# ═══════════════════════════════════════════════════════════════
# REDPANDA CLOUD SETUP (Serverless - Free $200 Credit)
# ═══════════════════════════════════════════════════════════════

# Step 1: Sign up
# Go to: https://redpanda.com/cloud
# Click "Start Free" → Create account

# Step 2: Create Serverless Cluster
# - Click "Create Cluster"
# - Choose "Serverless" (free tier)
# - Region: Choose closest to you
# - Name: "todo-kafka"

# Step 3: Create Topics
# In Redpanda Console:
# - Topics → Create Topic → "task-events" (3 partitions)
# - Topics → Create Topic → "reminders" (3 partitions)
# - Topics → Create Topic → "task-updates" (3 partitions)

# Step 4: Get Connection Details
# - Overview → Connection → Copy Bootstrap URL
# - Security → Users → Create user → Copy credentials

# Step 5: Create Kubernetes Secret
kubectl create secret generic kafka-secrets \
  --from-literal=brokers="your-cluster.cloud.redpanda.com:9092" \
  --from-literal=username="your-username" \
  --from-literal=password="your-password" \
  -n todo-app
```

### Dapr Component for Redpanda Cloud

```yaml
# dapr-components/pubsub-redpanda.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Redpanda Cloud connection
    - name: brokers
      secretKeyRef:
        name: kafka-secrets
        key: brokers

    # Authentication
    - name: authType
      value: "password"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"

    # TLS required for cloud
    - name: tlsEnable
      value: "true"

    # Consumer configuration
    - name: consumerGroup
      value: "todo-service"
    - name: initialOffset
      value: "oldest"

scopes:
  - backend-service
  - recurring-service
  - notification-service
```

### Option B: Strimzi (Self-Hosted on Kubernetes)

```bash
# ═══════════════════════════════════════════════════════════════
# STRIMZI SETUP (Self-Hosted on Minikube/K8s)
# ═══════════════════════════════════════════════════════════════

# Step 1: Create Kafka namespace
kubectl create namespace kafka

# Step 2: Install Strimzi Operator
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Step 3: Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

### Strimzi Kafka Cluster YAML

```yaml
# kafka/kafka-cluster.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1  # Use 3 in production
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      # Replication settings (adjust for production)
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
      # Performance tuning
      num.partitions: 3
      log.retention.hours: 168  # 7 days
    storage:
      type: ephemeral  # Use persistent-claim in production

  zookeeper:
    replicas: 1
    storage:
      type: ephemeral

  entityOperator:
    topicOperator: {}
    userOperator: {}
---
# kafka/kafka-topics.yaml
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-events
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 604800000  # 7 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: reminders
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 259200000  # 3 days
---
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: task-updates
  namespace: kafka
  labels:
    strimzi.io/cluster: todo-kafka
spec:
  partitions: 3
  replicas: 1
  config:
    retention.ms: 86400000  # 1 day
```

```bash
# Apply Kafka cluster and topics
kubectl apply -f kafka/kafka-cluster.yaml
kubectl apply -f kafka/kafka-topics.yaml

# Wait for Kafka
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka

# Verify
kubectl get kafka,kafkatopic -n kafka
```

### Dapr Component for Strimzi

```yaml
# dapr-components/pubsub-strimzi.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # Strimzi internal service
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"

    # No auth for internal cluster
    - name: authType
      value: "none"

    # Consumer configuration
    - name: consumerGroup
      value: "todo-service"
    - name: initialOffset
      value: "oldest"

scopes:
  - backend-service
  - recurring-service
  - notification-service
```

## Part 6: Idempotency & Error Handling

### 6.1 Idempotent Event Processing

```python
"""
Idempotent consumer pattern
[Task]: Handle at-least-once delivery
[Rule]: Process each event exactly once
"""

from functools import wraps
import hashlib

# In-memory cache for demo (use Redis in production)
processed_events = set()

def idempotent(func):
    """
    Decorator for idempotent event processing.

    [Spec]: Skip already-processed events based on event ID
    """
    @wraps(func)
    async def wrapper(event: dict, *args, **kwargs):
        event_id = event.get("id")

        if not event_id:
            # No ID = can't guarantee idempotency, process anyway
            return await func(event, *args, **kwargs)

        # Check if already processed
        event_hash = hashlib.sha256(event_id.encode()).hexdigest()

        if event_hash in processed_events:
            print(f"⏭️ Skipping duplicate event: {event_id}")
            return {"status": "DUPLICATE"}

        # Process event
        result = await func(event, *args, **kwargs)

        # Mark as processed
        processed_events.add(event_hash)

        return result

    return wrapper


@idempotent
async def process_task_event(event: dict):
    """Process task event idempotently"""
    event_type = event.get("type")
    data = event.get("data", {})

    if event_type == "com.taskmanager.task.completed":
        await handle_task_completed(data)

    return {"status": "SUCCESS"}
```

### 6.2 Dead Letter Queue Pattern

```yaml
# dapr-components/pubsub-with-dlq.yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"

    # Dead Letter Queue configuration
    - name: deadLetterTopic
      value: "dead-letters"
    - name: maxDeliveryAttempts
      value: "3"
```

```python
"""
Dead letter handler
[Task]: Process failed events from DLQ
"""

@app.post("/dead-letters")
async def handle_dead_letter(request: Request):
    """
    Handle events that failed processing 3 times.

    [Spec]: Log, alert, and store for manual review
    """
    failed_event = await request.json()

    # Log the failure
    print(f"💀 Dead letter received: {failed_event}")

    # Store for manual review
    await store_failed_event(failed_event)

    # Alert operations team
    await send_alert(
        title="Event Processing Failed",
        message=f"Event {failed_event.get('id')} failed after 3 attempts",
        severity="warning"
    )

    return {"status": "LOGGED"}
```

## Part 7: Testing Kafka Integration

```bash
# ═══════════════════════════════════════════════════════════════
# TESTING KAFKA VIA DAPR
# ═══════════════════════════════════════════════════════════════

# Test publishing (from inside a pod with Dapr sidecar)
kubectl exec -it <backend-pod> -c backend -n todo-app -- \
  curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/cloudevents+json" \
  -d '{
    "specversion": "1.0",
    "type": "com.taskmanager.task.created",
    "source": "/tasks/test",
    "id": "test-123",
    "time": "2024-01-15T10:00:00Z",
    "data": {"task_id": 1, "user_id": "test-user", "title": "Test Task"}
  }'

# Check consumer received it
kubectl logs -l app=recurring-service -n todo-app

# Check Kafka topics (Strimzi)
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Check consumer groups
kubectl exec -it todo-kafka-kafka-0 -n kafka -- \
  bin/kafka-consumer-groups.sh --list --bootstrap-server localhost:9092
```

## Summary

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Topics** | task-events, reminders, task-updates | Event channels |
| **Schema** | CloudEvents 1.0 | Standard format |
| **Publishing** | Dapr Pub/Sub | localhost:3500 |
| **Partitioning** | user_id as key | Ordering per user |
| **Platform** | Redpanda Cloud / Strimzi | Kafka backend |
| **Consumers** | Recurring, Notification services | Event handlers |
| **Reliability** | Idempotency + DLQ | At-least-once delivery |

### Quick Reference

```python
# Publish task event
await publish_task_created(task_id=1, user_id="user-123", title="Buy milk")

# Dapr endpoint
POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events

# Subscribe endpoint (in consumer service)
GET /dapr/subscribe → [{"pubsubname": "kafka-pubsub", "topic": "task-events", "route": "/events"}]
```
