# Skill: Kafka & Dapr Integration

## Purpose
Implement event-driven architecture using Kafka for message streaming and Dapr for distributed application runtime (pub/sub, state, secrets, jobs).

## Tech Stack
- **Kafka**: Event streaming (Strimzi on K8s or Redpanda Cloud)
- **Dapr**: Distributed app runtime
- **Strimzi**: Kubernetes operator for Kafka
- **Python**: aiokafka for direct Kafka access (optional)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                            │
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │ Backend Pod  │    │ Notif Pod    │    │ Recurring Pod│      │
│  │ ┌─────────┐  │    │ ┌─────────┐  │    │ ┌─────────┐  │      │
│  │ │ FastAPI │  │    │ │ Service │  │    │ │ Service │  │      │
│  │ └────┬────┘  │    │ └────┬────┘  │    │ └────┬────┘  │      │
│  │      │       │    │      │       │    │      │       │      │
│  │ ┌────▼────┐  │    │ ┌────▼────┐  │    │ ┌────▼────┐  │      │
│  │ │  Dapr   │  │    │ │  Dapr   │  │    │ │  Dapr   │  │      │
│  │ │ Sidecar │  │    │ │ Sidecar │  │    │ │ Sidecar │  │      │
│  │ └────┬────┘  │    │ └────┬────┘  │    │ └────┬────┘  │      │
│  └──────┼───────┘    └──────┼───────┘    └──────┼───────┘      │
│         │                   │                   │               │
│         └───────────────────┼───────────────────┘               │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │ DAPR COMPONENTS │                          │
│                    │  - PubSub (Kafka)                          │
│                    │  - State (Postgres)                        │
│                    │  - Jobs API                                │
│                    │  - Secrets (K8s)                           │
│                    └────────┬────────┘                          │
│                             │                                   │
│                    ┌────────▼────────┐                          │
│                    │  KAFKA CLUSTER  │                          │
│                    │ (Strimzi/Redpanda)                         │
│                    └─────────────────┘                          │
└─────────────────────────────────────────────────────────────────┘
```

## Part 1: Kafka Setup

### Option A: Strimzi (Self-Hosted on K8s)

**Install Strimzi Operator:**
```bash
# [Task]: T-090
# [From]: plan.md §9.1 - Kafka Setup

# Create namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka
```

**Create Kafka Cluster:**
```yaml
# kafka-cluster.yaml
# [Task]: T-091

apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 1  # Single node for hackathon (use 3+ in production)
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
      offsets.topic.replication.factor: 1
      transaction.state.log.replication.factor: 1
      transaction.state.log.min.isr: 1
      default.replication.factor: 1
      min.insync.replicas: 1
    storage:
      type: ephemeral  # Use persistent-claim in production
  zookeeper:
    replicas: 1
    storage:
      type: ephemeral
  entityOperator:
    topicOperator: {}
    userOperator: {}
```

```bash
# Apply
kubectl apply -f kafka-cluster.yaml

# Wait for Kafka
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=300s -n kafka
```

**Create Topics:**
```yaml
# kafka-topics.yaml
# [Task]: T-092

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
```

```bash
kubectl apply -f kafka-topics.yaml
```

### Option B: Redpanda Cloud (Managed)

1. Sign up at redpanda.com/cloud
2. Create Serverless cluster (free tier)
3. Create topics: `task-events`, `reminders`, `task-updates`
4. Get bootstrap URL and credentials

## Part 2: Dapr Setup

### Install Dapr on Kubernetes

```bash
# [Task]: T-093
# [From]: plan.md §9.2 - Dapr Installation

# Install Dapr CLI
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on K8s
dapr init -k

# Verify
dapr status -k
```

### Dapr Components

**1. Pub/Sub Component (Kafka):**
```yaml
# dapr-components/pubsub.yaml
# [Task]: T-094
# [From]: plan.md §9.3 - Dapr PubSub Configuration

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: todo-app
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    # For Strimzi
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-service"
    - name: authType
      value: "none"
    
    # For Redpanda Cloud (uncomment and update)
    # - name: brokers
    #   value: "your-cluster.cloud.redpanda.com:9092"
    # - name: authType
    #   value: "password"
    # - name: saslUsername
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: username
    # - name: saslPassword
    #   secretKeyRef:
    #     name: kafka-secrets
    #     key: password
```

**2. State Store Component (PostgreSQL):**
```yaml
# dapr-components/statestore.yaml
# [Task]: T-095

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: todo-secrets
        key: database-url
```

**3. Secrets Component (Kubernetes):**
```yaml
# dapr-components/secrets.yaml
# [Task]: T-096

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: todo-app
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

```bash
# Apply all components
kubectl apply -f dapr-components/
```

## Part 3: Publishing Events with Dapr

### Backend: Publish Task Events

```python
"""
backend/events.py - Event publishing via Dapr
[Task]: T-097
[From]: plan.md §9.4 - Event-Driven Architecture
"""

import httpx
import json
from datetime import datetime
from typing import Literal

DAPR_HTTP_PORT = 3500  # Dapr sidecar port
PUBSUB_NAME = "kafka-pubsub"

async def publish_task_event(
    event_type: Literal["created", "updated", "completed", "deleted"],
    task_id: int,
    user_id: str,
    task_data: dict
):
    """
    Publish task event to Kafka via Dapr PubSub.
    
    [Spec]: plan.md §9.4 - Event Schema
    """
    event = {
        "event_type": event_type,
        "task_id": task_id,
        "user_id": user_id,
        "task_data": task_data,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    try:
        # Publish via Dapr sidecar
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/task-events",
                json=event
            )
            response.raise_for_status()
            
    except Exception as e:
        print(f"Failed to publish event: {e}")
        # Don't fail the main operation if event publishing fails

async def publish_reminder_event(
    task_id: int,
    user_id: str,
    title: str,
    due_at: datetime,
    remind_at: datetime
):
    """
    Publish reminder event to Kafka via Dapr.
    
    [Spec]: plan.md §9.4 - Reminder Events
    """
    event = {
        "task_id": task_id,
        "user_id": user_id,
        "title": title,
        "due_at": due_at.isoformat(),
        "remind_at": remind_at.isoformat()
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/reminders",
                json=event
            )
            response.raise_for_status()
            
    except Exception as e:
        print(f"Failed to publish reminder: {e}")
```

### Use in MCP Tools

```python
"""
Update MCP tools to publish events
[Task]: T-098
"""

from mcp_tools.task_tools import mcp
from events import publish_task_event

@mcp.tool()
async def add_task(params: AddTaskParams) -> str:
    """Create task and publish event"""
    
    # Create task in database
    task = Task(
        user_id=params.user_id,
        title=params.title,
        description=params.description
    )
    session.add(task)
    await session.commit()
    
    # Publish event
    await publish_task_event(
        event_type="created",
        task_id=task.id,
        user_id=task.user_id,
        task_data={
            "title": task.title,
            "description": task.description
        }
    )
    
    return json.dumps({
        "task_id": task.id,
        "status": "created",
        "title": task.title
    })
```

## Part 4: Consuming Events with Dapr

### Notification Service

```python
"""
services/notification_service.py - Consume reminder events
[Task]: T-099
[From]: plan.md §9.5 - Notification Service
"""

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

class ReminderEvent(BaseModel):
    task_id: int
    user_id: str
    title: str
    due_at: str
    remind_at: str

@app.post("/reminders")
async def handle_reminder(event: Request):
    """
    Dapr calls this endpoint when a reminder event arrives.
    
    [Spec]: plan.md §9.5 - Pub/Sub Subscription
    """
    data = await event.json()
    
    # Extract event data
    reminder = ReminderEvent(**data["data"])
    
    # Send notification (implement your notification logic)
    print(f"📧 Sending reminder to {reminder.user_id}: {reminder.title}")
    
    # TODO: Send email/push notification
    # await send_email(reminder.user_id, reminder.title)
    
    return {"status": "SUCCESS"}

# Dapr subscription endpoint
@app.get("/dapr/subscribe")
async def subscribe():
    """
    Tell Dapr which topics to subscribe to.
    
    [Spec]: Dapr Pub/Sub pattern
    """
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "reminders",
            "route": "/reminders"
        }
    ]
```

### Recurring Task Service

```python
"""
services/recurring_service.py - Handle recurring tasks
[Task]: T-100
[From]: plan.md §9.6 - Recurring Task Engine
"""

from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/task-events")
async def handle_task_event(event: Request):
    """
    Listen for task completion events.
    If task is recurring, create next occurrence.
    
    [Spec]: plan.md §9.6 - Recurring Logic
    """
    data = await event.json()
    event_data = data["data"]
    
    if event_data["event_type"] == "completed":
        task_id = event_data["task_id"]
        
        # Check if task is recurring
        task = await get_task(task_id)
        
        if task.recurring:
            # Create next occurrence
            next_task = await create_next_occurrence(task)
            print(f"✅ Created next occurrence: {next_task.id}")
    
    return {"status": "SUCCESS"}

@app.get("/dapr/subscribe")
async def subscribe():
    return [
        {
            "pubsubname": "kafka-pubsub",
            "topic": "task-events",
            "route": "/task-events"
        }
    ]
```

## Part 5: Dapr Jobs API (Scheduled Reminders)

```python
"""
Schedule reminder using Dapr Jobs API
[Task]: T-101
[From]: plan.md §9.7 - Scheduled Reminders
"""

import httpx
from datetime import datetime

async def schedule_reminder(task_id: int, remind_at: datetime, user_id: str):
    """
    Schedule a reminder to fire at exact time using Dapr Jobs API.
    
    [Spec]: plan.md §9.7 - No polling, exact timing
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://localhost:3500/v1.0-alpha1/jobs/reminder-task-{task_id}",
            json={
                "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "data": {
                    "task_id": task_id,
                    "user_id": user_id,
                    "type": "reminder"
                }
            }
        )
        response.raise_for_status()

# Handle job callback
@app.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """
    Dapr calls this when the scheduled job fires.
    
    [Spec]: Exact timing trigger
    """
    job_data = await request.json()
    
    if job_data["data"]["type"] == "reminder":
        # Publish reminder event
        await publish_event(
            "reminders",
            "reminder.due",
            job_data["data"]
        )
    
    return {"status": "SUCCESS"}
```

## Part 6: Deployment with Dapr

### Update Deployments to Include Dapr Sidecar

```yaml
# Add Dapr annotations to deployments
# [Task]: T-102

apiVersion: apps/v1
kind: Deployment
metadata:
  name: todo-backend
spec:
  template:
    metadata:
      labels:
        app: todo-backend
      annotations:
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
    spec:
      containers:
      - name: backend
        image: your-dockerhub/todo-backend:latest
        # ... rest of container spec
```

### Deploy Services

```bash
# Deploy all services with Dapr
kubectl apply -f deployments/
kubectl apply -f dapr-components/

# Check Dapr components
dapr components -k -n todo-app

# Check logs
kubectl logs -l app=todo-backend -c daprd -n todo-app
```

## Testing Event Flow

```bash
# Test event publishing
curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"event_type": "created", "task_id": 1, "user_id": "test"}'

# Check if consumer received it
kubectl logs -l app=notification-service -n todo-app
```

## Summary

This skill provides:
- ✅ Kafka setup (Strimzi or Redpanda)
- ✅ Dapr installation and configuration
- ✅ Pub/Sub event-driven architecture
- ✅ State management with Dapr
- ✅ Jobs API for scheduled tasks
- ✅ Multiple microservices (backend, notification, recurring)
- ✅ Decoupled, scalable architecture
- ✅ Production-ready patterns