# Data Model: Phase V Part B - Local Minikube + Dapr + Kafka

**Feature ID**: 006-phase5-partb-local-deployment
**Created**: 2026-02-04

---

## 1. Overview

Part B focuses on infrastructure deployment, not data model changes. The application data model from Phase V Part A remains unchanged. This document describes the **infrastructure entities** being deployed.

---

## 2. Infrastructure Entities

### 2.1 Kubernetes Resources

#### Deployments

| Entity | Namespace | Containers | Purpose |
|--------|-----------|------------|---------|
| todo-backend | default | backend, daprd | FastAPI + Dapr sidecar |
| todo-frontend | default | frontend, daprd | Next.js + Dapr sidecar |
| redpanda | default | redpanda | Kafka-compatible broker |

#### Services

| Entity | Type | Ports | Purpose |
|--------|------|-------|---------|
| todo-backend | ClusterIP | 8000 | Backend API |
| todo-frontend | NodePort | 3000 | Frontend web |
| redpanda | ClusterIP | 9092 | Kafka broker |

#### Secrets

| Entity | Keys | Purpose |
|--------|------|---------|
| db-secrets | connection-string | Neon PostgreSQL URL |
| api-secrets | cohere-api-key, gemini-api-key, better-auth-secret | API credentials |

### 2.2 Dapr Components

| Entity | Type | Scope | Purpose |
|--------|------|-------|---------|
| kafka-pubsub | pubsub.kafka | todo-backend | Event publishing |
| statestore | state.postgresql | todo-backend | Session caching |
| kubernetes-secrets | secretstores.kubernetes | todo-backend, todo-frontend | Secret access |

---

## 3. Kafka Topics

### 3.1 Topic: task-events

**Purpose**: Task lifecycle events

| Field | Type | Description |
|-------|------|-------------|
| specversion | string | "1.0" (CloudEvents) |
| type | string | Event type |
| source | string | "/todo-backend/tasks" |
| id | string | UUID |
| time | string | ISO 8601 timestamp |
| data | object | Event payload |

**Event Types**:
- `com.todo.task.created`
- `com.todo.task.updated`
- `com.todo.task.completed`
- `com.todo.task.deleted`

### 3.2 Topic: reminders

**Purpose**: Reminder and recurring task events

**Event Types**:
- `com.todo.recurring.triggered`
- `com.todo.reminder.due`

---

## 4. Dapr State Store Schema

### 4.1 Session State

**Key Pattern**: `session-{user_id}-{conversation_id}`

```json
{
  "user_id": "string",
  "conversation_id": "string",
  "messages": [
    {
      "role": "user|assistant",
      "content": "string",
      "timestamp": "ISO 8601"
    }
  ],
  "created_at": "ISO 8601",
  "last_updated": "ISO 8601"
}
```

### 4.2 Cache State

**Key Pattern**: `cache-{resource}-{id}`

```json
{
  "data": "any",
  "ttl": "integer (seconds)",
  "created_at": "ISO 8601"
}
```

---

## 5. Configuration Values

### 5.1 values-dapr.yaml Schema

```yaml
dapr:
  enabled: boolean          # Enable Dapr sidecars
  logLevel: string          # debug|info|warn|error

backend:
  dapr:
    enabled: boolean
    appId: string           # "todo-backend"
    appPort: integer        # 8000
    enableApiLogging: boolean

frontend:
  dapr:
    enabled: boolean
    appId: string           # "todo-frontend"
    appPort: integer        # 3000

kafka:
  enabled: boolean
  broker: string            # "redpanda" | "strimzi"

redpanda:
  enabled: boolean
  image:
    repository: string
    tag: string
  resources:
    limits:
      memory: string
      cpu: string
  service:
    type: string            # ClusterIP
    port: integer           # 9092
```

---

## 6. Entity Relationships

```
┌─────────────────────────────────────────────────────────────┐
│                    KUBERNETES CLUSTER                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐     invokes     ┌─────────────┐           │
│  │  Frontend   │────────────────▶│   Backend   │           │
│  │  Deployment │                 │  Deployment │           │
│  └──────┬──────┘                 └──────┬──────┘           │
│         │                               │                   │
│         │ sidecar                       │ sidecar          │
│         ▼                               ▼                   │
│  ┌─────────────┐                 ┌─────────────┐           │
│  │  Dapr Pod   │                 │  Dapr Pod   │           │
│  │  (daprd)    │                 │  (daprd)    │           │
│  └─────────────┘                 └──────┬──────┘           │
│                                         │                   │
│                               publishes │                   │
│                                         ▼                   │
│                              ┌──────────────────┐          │
│                              │   kafka-pubsub   │          │
│                              │    Component     │          │
│                              └────────┬─────────┘          │
│                                       │                     │
│                                       ▼                     │
│                              ┌──────────────────┐          │
│                              │    Redpanda      │          │
│                              │    (Kafka)       │          │
│                              └──────────────────┘          │
│                                       │                     │
│                              ┌────────┴────────┐           │
│                              ▼                 ▼           │
│                        ┌──────────┐     ┌──────────┐       │
│                        │ task-    │     │reminders │       │
│                        │ events   │     │  topic   │       │
│                        │  topic   │     │          │       │
│                        └──────────┘     └──────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                                │
                                │ external
                                ▼
                    ┌──────────────────────┐
                    │   Neon PostgreSQL    │
                    │   (Main Database)    │
                    └──────────────────────┘
```

---

## 7. Resource Requirements Summary

| Resource Type | Count | Memory | CPU |
|---------------|-------|--------|-----|
| Deployments | 3 | ~2GB | ~2 cores |
| Services | 3 | N/A | N/A |
| ConfigMaps | 1 | N/A | N/A |
| Secrets | 2 | N/A | N/A |
| Dapr Components | 3 | N/A | N/A |
| Kafka Topics | 2 | N/A | N/A |

**Total Cluster Requirement**: 4GB RAM, 2 CPUs (Minikube default)

---

## 8. Validation Rules

### 8.1 Deployment Validation

- All pods must have 2/2 containers (app + sidecar)
- All pods must be in Running state
- No CrashLoopBackOff states

### 8.2 Dapr Component Validation

- Components must appear in `kubectl get components.dapr.io`
- Sidecar logs must show "component loaded" messages
- No authentication errors in logs

### 8.3 Kafka Validation

- Broker must be reachable at port 9092
- Topics must exist (auto-created or manual)
- Messages must be consumable via `rpk`
