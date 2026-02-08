# Skill: Dapr Sidecar Integration

## Purpose
Add Dapr (Distributed Application Runtime) to applications for event-driven, stateless, and portable distributed features. All application-to-infrastructure communication goes through the Dapr sidecar.

## Tech Stack
- **Dapr**: Distributed application runtime
- **Dapr Sidecar**: localhost:3500 (HTTP) / localhost:50001 (gRPC)
- **Building Blocks**: pubsub, state, jobs, secrets, service-invocation
- **Infrastructure**: Kafka (via pubsub.kafka), PostgreSQL (via state.postgresql)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                       APPLICATION POD                            │
│                                                                  │
│  ┌─────────────────────┐      ┌─────────────────────┐          │
│  │     Application     │      │    Dapr Sidecar     │          │
│  │                     │      │                     │          │
│  │  - FastAPI Backend  │◄────►│  - HTTP: :3500      │          │
│  │  - MCP Tools        │      │  - gRPC: :50001     │          │
│  │  - Business Logic   │      │  - Metrics: :9090   │          │
│  │                     │      │                     │          │
│  └─────────────────────┘      └──────────┬──────────┘          │
│                                          │                      │
└──────────────────────────────────────────┼──────────────────────┘
                                           │
                    ┌──────────────────────┼──────────────────────┐
                    │                      ▼                      │
                    │           DAPR COMPONENTS                   │
                    │                                             │
                    │  ┌─────────────┐  ┌─────────────┐          │
                    │  │ pubsub.kafka│  │state.postgres│          │
                    │  └──────┬──────┘  └──────┬──────┘          │
                    │         │                │                  │
                    │  ┌──────▼──────┐  ┌──────▼──────┐          │
                    │  │   Kafka     │  │ PostgreSQL  │          │
                    │  │   Cluster   │  │  Database   │          │
                    │  └─────────────┘  └─────────────┘          │
                    │                                             │
                    │  ┌─────────────┐  ┌─────────────┐          │
                    │  │  Jobs API   │  │  Secrets    │          │
                    │  │ (Scheduler) │  │ (K8s Store) │          │
                    │  └─────────────┘  └─────────────┘          │
                    └─────────────────────────────────────────────┘
```

## Rule #1: ALWAYS Use Dapr Sidecar

```
❌ WRONG - Direct Infrastructure Access
──────────────────────────────────────
from kafka import KafkaProducer
producer = KafkaProducer(bootstrap_servers='kafka:9092')
producer.send('task-events', value=event)

✅ CORRECT - Via Dapr Sidecar
──────────────────────────────────────
import httpx
await httpx.post(
    "http://localhost:3500/v1.0/publish/kafka-pubsub/task-events",
    json=event
)
```

## Part 1: Dapr Installation

### Install Dapr on Kubernetes

```bash
# [Task]: Install Dapr CLI
# For Linux/macOS
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# For Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Initialize Dapr on Kubernetes
dapr init -k

# Verify installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION
#   dapr-dashboard         dapr-system  True     Running  1         0.14.0
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.13.0
#   dapr-operator          dapr-system  True     Running  1         1.13.0
#   dapr-placement-server  dapr-system  True     Running  1         1.13.0
#   dapr-sentry            dapr-system  True     Running  1         1.13.0
```

### Install Dapr for Local Development

```bash
# Initialize Dapr locally (uses containers)
dapr init

# Run application with Dapr sidecar
dapr run --app-id backend-service --app-port 8000 -- uvicorn main:app
```

## Part 2: Dapr Component YAML Files

### 2.1 Pub/Sub Component (Kafka)

```yaml
# dapr-components/pubsub.yaml
# [Task]: Configure Kafka as Pub/Sub backend
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
    # Kafka broker connection
    - name: brokers
      value: "todo-kafka-kafka-bootstrap.kafka.svc.cluster.local:9092"

    # Consumer group for this application
    - name: consumerGroup
      value: "todo-service"

    # Authentication (none for internal cluster)
    - name: authType
      value: "none"

    # For Redpanda Cloud or secured Kafka:
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
    # - name: saslMechanism
    #   value: "SCRAM-SHA-256"

scopes:
  - backend-service
  - notification-service
  - recurring-service
```

### 2.2 State Store Component (PostgreSQL)

```yaml
# dapr-components/statestore.yaml
# [Task]: Configure PostgreSQL as State Store
# [From]: plan.md §9.4 - Conversation State Management

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: todo-app
spec:
  type: state.postgresql
  version: v1
  metadata:
    # Connection string from secret
    - name: connectionString
      secretKeyRef:
        name: todo-secrets
        key: database-url

    # Table name for state storage
    - name: tableName
      value: "dapr_state"

    # Key prefix for multi-tenancy
    - name: keyPrefix
      value: "todo"

scopes:
  - backend-service
```

### 2.3 Secrets Component (Kubernetes)

```yaml
# dapr-components/secrets.yaml
# [Task]: Enable Kubernetes secrets access

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

### 2.4 Jobs Component (Scheduled Tasks)

```yaml
# dapr-components/scheduler.yaml
# [Task]: Enable Jobs API for scheduled reminders
# [From]: plan.md §9.7 - Scheduled Reminders

apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: scheduler
  namespace: todo-app
spec:
  type: scheduler.kubernetes
  version: v1
  metadata: []

scopes:
  - backend-service
```

### Apply Components

```bash
# Create namespace
kubectl create namespace todo-app

# Apply all Dapr components
kubectl apply -f dapr-components/

# Verify components
dapr components -k -n todo-app

# Expected:
#   NAMESPACE  NAME               TYPE                  VERSION
#   todo-app   kafka-pubsub       pubsub.kafka          v1
#   todo-app   statestore         state.postgresql      v1
#   todo-app   kubernetes-secrets secretstores.kubernetes v1
#   todo-app   scheduler          scheduler.kubernetes  v1
```

## Part 3: Publishing Events via Dapr Pub/Sub

### 3.1 Event Publisher Module

```python
"""
backend/services/event_publisher.py
[Task]: Publish events through Dapr sidecar
[Rule]: NEVER use direct Kafka client
"""

import httpx
import json
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel

# Dapr sidecar configuration
DAPR_HTTP_PORT = 3500
PUBSUB_NAME = "kafka-pubsub"

class TaskEvent(BaseModel):
    """CloudEvents-compatible task event schema"""
    specversion: str = "1.0"
    type: str
    source: str = "/tasks/backend-service"
    id: str
    time: str
    datacontenttype: str = "application/json"
    data: dict

async def publish_event(
    topic: str,
    event_type: str,
    data: dict,
    event_id: Optional[str] = None
) -> bool:
    """
    Publish event to Kafka topic via Dapr sidecar.

    [Spec]: All events use CloudEvents format
    [Rule]: Use localhost:3500 Dapr endpoint only

    Args:
        topic: Kafka topic name (task-events, reminders, task-updates)
        event_type: Event type (com.taskmanager.task.created, etc.)
        data: Event payload
        event_id: Optional event ID (auto-generated if not provided)

    Returns:
        True if published successfully
    """
    import uuid

    event = TaskEvent(
        type=event_type,
        id=event_id or str(uuid.uuid4()),
        time=datetime.utcnow().isoformat() + "Z",
        data=data
    )

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/publish/{PUBSUB_NAME}/{topic}",
                json=event.model_dump(),
                headers={"Content-Type": "application/cloudevents+json"}
            )
            response.raise_for_status()
            return True

    except httpx.HTTPStatusError as e:
        print(f"Failed to publish event: {e.response.status_code} - {e.response.text}")
        return False
    except Exception as e:
        print(f"Event publishing error: {e}")
        return False


# Convenience functions for common events
async def publish_task_created(task_id: int, user_id: str, title: str, **extra):
    """Publish task.created event"""
    return await publish_event(
        topic="task-events",
        event_type="com.taskmanager.task.created",
        data={"task_id": task_id, "user_id": user_id, "title": title, **extra}
    )

async def publish_task_updated(task_id: int, user_id: str, changes: dict):
    """Publish task.updated event"""
    return await publish_event(
        topic="task-events",
        event_type="com.taskmanager.task.updated",
        data={"task_id": task_id, "user_id": user_id, "changes": changes}
    )

async def publish_task_completed(task_id: int, user_id: str):
    """Publish task.completed event"""
    return await publish_event(
        topic="task-events",
        event_type="com.taskmanager.task.completed",
        data={"task_id": task_id, "user_id": user_id}
    )

async def publish_task_deleted(task_id: int, user_id: str):
    """Publish task.deleted event"""
    return await publish_event(
        topic="task-events",
        event_type="com.taskmanager.task.deleted",
        data={"task_id": task_id, "user_id": user_id}
    )

async def publish_reminder(task_id: int, user_id: str, title: str, due_at: datetime, remind_at: datetime):
    """Publish reminder event"""
    return await publish_event(
        topic="reminders",
        event_type="com.taskmanager.reminder.due",
        data={
            "task_id": task_id,
            "user_id": user_id,
            "title": title,
            "due_at": due_at.isoformat(),
            "remind_at": remind_at.isoformat()
        }
    )
```

### 3.2 Integrate with MCP Tools

```python
"""
Update MCP tools to publish events
[Task]: Event integration with task CRUD
"""

from services.event_publisher import (
    publish_task_created,
    publish_task_completed,
    publish_task_deleted
)

@mcp.tool()
async def add_task(user_id: str, title: str, description: str = "") -> str:
    """Create task and publish event"""

    # 1. Create in database
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    await session.commit()

    # 2. Publish event (non-blocking, don't fail if event fails)
    await publish_task_created(
        task_id=task.id,
        user_id=user_id,
        title=title,
        description=description
    )

    return json.dumps({"task_id": task.id, "status": "created"})

@mcp.tool()
async def complete_task(user_id: str, task_id: int) -> str:
    """Complete task and publish event"""

    # 1. Update in database
    task = await get_task_for_user(task_id, user_id)
    task.completed = True
    await session.commit()

    # 2. Publish event
    await publish_task_completed(task_id=task_id, user_id=user_id)

    return json.dumps({"task_id": task_id, "status": "completed"})
```

## Part 4: State Management via Dapr

### 4.1 Conversation State Manager

```python
"""
backend/services/state_manager.py
[Task]: Store conversation history via Dapr State API
[Rule]: Use Dapr state store, not direct database
"""

import httpx
import json
from typing import List, Optional
from pydantic import BaseModel

DAPR_HTTP_PORT = 3500
STATE_STORE = "statestore"

class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: str

class ConversationState(BaseModel):
    user_id: str
    conversation_id: str
    messages: List[Message]
    created_at: str
    updated_at: str


async def get_conversation(user_id: str, conversation_id: str) -> Optional[ConversationState]:
    """
    Get conversation state from Dapr state store.

    [Spec]: Stateless backend - all state from external store
    """
    key = f"conversation-{user_id}-{conversation_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATE_STORE}/{key}"
            )

            if response.status_code == 204:  # No content = not found
                return None

            response.raise_for_status()
            data = response.json()
            return ConversationState(**data)

    except Exception as e:
        print(f"Failed to get state: {e}")
        return None


async def save_conversation(state: ConversationState) -> bool:
    """
    Save conversation state to Dapr state store.

    [Spec]: Atomic state updates
    """
    key = f"conversation-{state.user_id}-{state.conversation_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0/state/{STATE_STORE}",
                json=[{
                    "key": key,
                    "value": state.model_dump()
                }]
            )
            response.raise_for_status()
            return True

    except Exception as e:
        print(f"Failed to save state: {e}")
        return False


async def append_message(
    user_id: str,
    conversation_id: str,
    role: str,
    content: str
) -> bool:
    """Append a message to conversation history"""
    from datetime import datetime

    # Get current state
    state = await get_conversation(user_id, conversation_id)

    if state is None:
        # Create new conversation
        state = ConversationState(
            user_id=user_id,
            conversation_id=conversation_id,
            messages=[],
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )

    # Append message
    state.messages.append(Message(
        role=role,
        content=content,
        timestamp=datetime.utcnow().isoformat()
    ))
    state.updated_at = datetime.utcnow().isoformat()

    # Save updated state
    return await save_conversation(state)
```

## Part 5: Dapr Jobs API (Scheduled Reminders)

### 5.1 Schedule Exact-Time Reminders

```python
"""
backend/services/reminder_scheduler.py
[Task]: Schedule reminders using Dapr Jobs API
[From]: plan.md §9.7 - No polling, exact timing
"""

import httpx
from datetime import datetime
from typing import Optional

DAPR_HTTP_PORT = 3500

async def schedule_reminder(
    task_id: int,
    user_id: str,
    title: str,
    remind_at: datetime
) -> bool:
    """
    Schedule a reminder to fire at exact time.

    [Spec]: Uses Dapr Jobs API for exact-time scheduling
    [Rule]: No polling loops, no cron jobs

    Args:
        task_id: ID of the task
        user_id: User to notify
        title: Reminder title
        remind_at: Exact time to trigger

    Returns:
        True if scheduled successfully
    """
    job_name = f"reminder-{task_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}",
                json={
                    # Exact time to trigger (ISO 8601 format)
                    "dueTime": remind_at.strftime("%Y-%m-%dT%H:%M:%SZ"),

                    # Data passed to callback
                    "data": {
                        "task_id": task_id,
                        "user_id": user_id,
                        "title": title,
                        "type": "reminder"
                    }
                }
            )
            response.raise_for_status()
            return True

    except Exception as e:
        print(f"Failed to schedule reminder: {e}")
        return False


async def cancel_reminder(task_id: int) -> bool:
    """Cancel a scheduled reminder"""
    job_name = f"reminder-{task_id}"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"http://localhost:{DAPR_HTTP_PORT}/v1.0-alpha1/jobs/{job_name}"
            )
            response.raise_for_status()
            return True

    except Exception as e:
        print(f"Failed to cancel reminder: {e}")
        return False
```

### 5.2 Job Callback Handler

```python
"""
backend/api/jobs.py
[Task]: Handle Dapr job triggers
"""

from fastapi import APIRouter, Request
from services.event_publisher import publish_reminder

router = APIRouter()

@router.post("/api/jobs/trigger")
async def handle_job_trigger(request: Request):
    """
    Dapr calls this endpoint when a scheduled job fires.

    [Spec]: Exact-time reminder trigger
    """
    job_data = await request.json()

    if job_data.get("data", {}).get("type") == "reminder":
        data = job_data["data"]

        # Publish reminder event to Kafka
        await publish_reminder(
            task_id=data["task_id"],
            user_id=data["user_id"],
            title=data["title"],
            due_at=datetime.fromisoformat(data.get("due_at", datetime.utcnow().isoformat())),
            remind_at=datetime.utcnow()
        )

        print(f"Reminder triggered for task {data['task_id']}")

    return {"status": "SUCCESS"}
```

## Part 6: Service Invocation (Frontend → Backend)

### 6.1 Service-to-Service Calls

```python
"""
Using Dapr service invocation for resilient calls
[Task]: Frontend backend calls with automatic retries
"""

import httpx

async def invoke_backend_service(method: str, endpoint: str, data: dict = None):
    """
    Call backend service via Dapr service invocation.

    Benefits:
    - Automatic retries
    - Circuit breaker
    - mTLS encryption
    - Service discovery
    """
    try:
        async with httpx.AsyncClient() as client:
            url = f"http://localhost:3500/v1.0/invoke/backend-service/method/{endpoint}"

            if method.upper() == "GET":
                response = await client.get(url)
            else:
                response = await client.post(url, json=data)

            response.raise_for_status()
            return response.json()

    except Exception as e:
        print(f"Service invocation failed: {e}")
        raise
```

## Part 7: Helm Annotations for Dapr Sidecar

### 7.1 Deployment with Dapr Sidecar

```yaml
# helm/backend/templates/deployment.yaml
# [Task]: Inject Dapr sidecar via Helm annotations

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-backend
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Release.Name }}-backend
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-backend
      annotations:
        # Dapr sidecar injection
        dapr.io/enabled: "true"
        dapr.io/app-id: "backend-service"
        dapr.io/app-port: "8000"
        dapr.io/log-level: "info"
        dapr.io/enable-api-logging: "true"

        # Optional: Configure sidecar resources
        dapr.io/sidecar-cpu-request: "100m"
        dapr.io/sidecar-memory-request: "64Mi"
        dapr.io/sidecar-cpu-limit: "500m"
        dapr.io/sidecar-memory-limit: "256Mi"

    spec:
      containers:
      - name: backend
        image: {{ .Values.image.repository }}:{{ .Values.image.tag }}
        ports:
        - containerPort: 8000
        env:
        - name: DAPR_HTTP_PORT
          value: "3500"
        - name: DAPR_GRPC_PORT
          value: "50001"
```

### 7.2 Values for Dapr Configuration

```yaml
# helm/backend/values.yaml

replicaCount: 1

image:
  repository: your-registry/todo-backend
  tag: latest

dapr:
  enabled: true
  appId: backend-service
  appPort: 8000
  logLevel: info

  # Sidecar resources
  sidecar:
    cpu:
      request: 100m
      limit: 500m
    memory:
      request: 64Mi
      limit: 256Mi
```

## Part 8: Troubleshooting Dapr

### 8.1 Check Sidecar Status

```bash
# Check if sidecar is running
kubectl get pods -n todo-app -o jsonpath='{.items[*].spec.containers[*].name}'

# Should show both: backend daprd

# Check sidecar logs
kubectl logs -l app=backend -c daprd -n todo-app

# Check application logs
kubectl logs -l app=backend -c backend -n todo-app

# Verify Dapr health
kubectl exec -it <pod-name> -c daprd -n todo-app -- wget -qO- http://localhost:3500/v1.0/healthz
```

### 8.2 Debug Component Connections

```bash
# List components
dapr components -k -n todo-app

# Check component logs
kubectl logs -l app=dapr-operator -n dapr-system

# Test pubsub manually
kubectl exec -it <pod-name> -c backend -n todo-app -- \
  curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/test-topic \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

### 8.3 Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Sidecar not starting | Missing annotations | Add `dapr.io/enabled: "true"` |
| Component not found | Wrong namespace | Ensure components in same namespace |
| Connection refused | Sidecar not ready | Wait for sidecar readiness |
| Auth failures | Missing secrets | Create K8s secrets for credentials |
| Event not delivered | Wrong topic | Check pubsub component scopes |

## Summary

This skill provides complete Dapr integration:

| Capability | Dapr API | Use Case |
|------------|----------|----------|
| **Pub/Sub** | `/v1.0/publish/{pubsub}/{topic}` | Event-driven messaging |
| **State** | `/v1.0/state/{store}` | Conversation history |
| **Jobs** | `/v1.0-alpha1/jobs/{name}` | Scheduled reminders |
| **Secrets** | `/v1.0/secrets/{store}/{key}` | Credential access |
| **Invocation** | `/v1.0/invoke/{app}/method/{endpoint}` | Service calls |

**Key Rules:**
1. ALL infrastructure access through Dapr sidecar (localhost:3500)
2. NEVER use direct Kafka, Redis, or database clients
3. Use YAML components for configuration
4. Enable sidecar via Helm annotations
5. Events use CloudEvents format
