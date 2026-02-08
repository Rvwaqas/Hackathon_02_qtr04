# Phase V: Advanced Features & Event-Driven Architecture

## Overview

Phase V extends the AI Todo Chatbot with advanced task management features and event-driven architecture using Dapr Pub/Sub.

**Part A**: Code-level implementation of features and event publishing patterns.
**Part B**: Local Minikube deployment with Dapr sidecars, Kafka (Redpanda), and all 5 Dapr building blocks.
**Part C (Current)**: Cloud deployment on Oracle OKE (Always Free) with Redpanda Cloud Kafka, GitHub Actions CI/CD, and public LoadBalancer — $0 cost.

## Part A Features

### Intermediate Features

#### Priority Levels
Tasks support priority levels: `high`, `medium`, `low`, `none`.

**Chatbot Commands:**
```
"add high priority task meeting"
"add urgent task deadline"
"add low priority task organize files"
"show high priority tasks"
"sort by priority"
```

#### Tags/Categories
Tasks can have multiple tags for organization.

**Chatbot Commands:**
```
"add task report tagged work"
"add task groceries tagged personal shopping"
"show tasks tagged work"
"find tasks with tag urgent"
```

#### Search, Filter & Sort
Find and organize tasks with powerful filtering.

**Chatbot Commands:**
```
"find tasks about meeting"
"search for groceries"
"show pending tasks"
"show completed tasks"
"show high priority tasks tagged work"
"sort by due date"
"sort by priority descending"
"show tasks sorted by title"
```

### Advanced Features

#### Recurring Tasks
Tasks can repeat on a schedule.

**Chatbot Commands:**
```
"add task standup repeat daily"
"add task review repeat weekly"
"add task report repeat monthly"
"make task 5 repeat weekly until March 31"
```

**Behavior:**
- Completing a recurring task automatically creates the next occurrence
- Next occurrence inherits all properties (tags, priority, reminders)
- Supports custom intervals (every 2 weeks, every 3 days)

#### Due Dates
Set deadlines for tasks.

**Chatbot Commands:**
```
"add task report due Friday"
"add task meeting due tomorrow"
"add task deadline due in 3 days"
"sort by due date"
```

#### Reminders
Get reminded before task due dates.

**Chatbot Commands:**
```
"add task meeting remind me 30 minutes before"
"add task call remind me 1 hour before"
"add task deadline remind me 1 day before"
```

### Event-Driven Architecture

Phase V Part A implements CloudEvents 1.0 compliant event publishing via Dapr Pub/Sub.

#### Event Types

| Event Type | Topic | Trigger |
|------------|-------|---------|
| `com.todo.task.created` | task-events | Task created |
| `com.todo.task.updated` | task-events | Task modified |
| `com.todo.task.completed` | task-events | Task marked complete |
| `com.todo.task.deleted` | task-events | Task removed |
| `com.todo.recurring.triggered` | reminders | Recurring task creates next |
| `com.todo.reminder.due` | reminders | Reminder time reached |

#### CloudEvents Schema

```json
{
  "specversion": "1.0",
  "type": "com.todo.task.created",
  "source": "/api/tasks",
  "id": "uuid-v4",
  "time": "2026-02-01T10:00:00Z",
  "datacontenttype": "application/json",
  "data": {
    "task_id": 1,
    "user_id": 1,
    "title": "Task title",
    "priority": "high",
    "tags": ["work"],
    "due_date": "2026-02-07T17:00:00Z"
  }
}
```

#### Graceful Degradation

Event publishing is fire-and-forget:
- If Dapr sidecar is unavailable, events are logged but operations continue
- Task CRUD operations always succeed regardless of event publishing status
- Errors are logged for debugging but never block user operations

## API Reference

### Filter Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter: `pending`, `completed`, `all` |
| `priority` | string | Filter: `high`, `medium`, `low`, `none`, `all` |
| `tag` | string | Filter by single tag name |
| `search` | string | Keyword search in title/description |
| `sort` | string | Sort by: `created_at`, `due_date`, `priority`, `title` |
| `order` | string | Sort order: `asc`, `desc` |

### Example API Calls

```bash
# Get high priority pending tasks
GET /api/tasks?status=pending&priority=high

# Search for meeting-related tasks
GET /api/tasks?search=meeting

# Get work-tagged tasks sorted by due date
GET /api/tasks?tag=work&sort=due_date&order=asc

# Combined filters
GET /api/tasks?status=pending&priority=high&tag=work&sort=due_date
```

### Create Task with Advanced Features

```bash
POST /api/tasks
{
  "title": "Weekly Report",
  "description": "Submit weekly status report",
  "priority": "high",
  "tags": ["work", "reports"],
  "due_date": "2026-02-07T17:00:00Z",
  "recurrence": {
    "type": "weekly",
    "interval": 1
  },
  "reminder_offset_minutes": 60
}
```

## Testing

Run the test suite:

```bash
cd backend
pytest tests/ -v

# Specific test categories
pytest tests/test_filters.py -v      # Filter/sort tests
pytest tests/test_events.py -v       # Event publishing tests
pytest tests/test_recurring.py -v    # Recurring task tests
pytest tests/test_chatbot_intents.py -v  # Intent recognition tests
```

## Backward Compatibility

All Phase III functionality is preserved:
- Basic task CRUD operations unchanged
- Existing chatbot commands work as before
- Conversation history maintained
- User isolation enforced

## Specifications

- **Spec Document**: `specs/005-phase5-parta-advanced-events/spec.md`
- **Implementation Plan**: `specs/005-phase5-parta-advanced-events/plan.md`
- **Task Breakdown**: `specs/005-phase5-parta-advanced-events/tasks.md`
- **Event Schema**: `specs/005-phase5-parta-advanced-events/contracts/event-schema.md`
- **MCP Tools**: `specs/005-phase5-parta-advanced-events/contracts/mcp-tools.md`

## Part B: Local Minikube + Dapr + Kafka Deployment

Phase V Part B deploys the complete application on Minikube with full Dapr runtime and Kafka (Redpanda).

### Deployment Architecture

```
MINIKUBE CLUSTER
├── dapr-system (operator, sidecar-injector, placement, sentry)
├── default namespace
│   ├── todo-backend    [FastAPI + Dapr sidecar]  2/2
│   ├── todo-frontend   [Next.js + Dapr sidecar]  2/2
│   ├── redpanda        [Kafka broker]             1/1
│   └── Dapr Components: kafka-pubsub, statestore, kubernetes-secrets
└── External: Neon PostgreSQL
```

### 5 Dapr Building Blocks

| Building Block | Component | Usage |
|----------------|-----------|-------|
| Pub/Sub | kafka-pubsub | Task events to Kafka |
| State Store | statestore | Session caching via PostgreSQL |
| Secrets | kubernetes-secrets | API key management |
| Jobs | Built-in | Reminder scheduling |
| Service Invocation | Built-in | Frontend-to-backend calls |

### Quick Deploy

```bash
# 1. Start Minikube + Dapr
minikube start --memory=4096 --cpus=2 --driver=docker
dapr init -k --wait

# 2. Build images
eval $(minikube docker-env)
docker build -t todo-backend:latest -f phase5/docker/Dockerfile.backend phase5/
docker build -t todo-frontend:latest -f phase5/docker/Dockerfile.frontend phase5/

# 3. Create secrets
kubectl create secret generic todo-chatbot-secrets \
  --from-literal=database-url="YOUR_DB_URL" \
  --from-literal=cohere-api-key="YOUR_KEY" \
  --from-literal=jwt-secret="YOUR_SECRET"

# 4. Deploy
helm upgrade --install todo-chatbot phase5/helm/todo-chatbot \
  -f phase5/helm/todo-chatbot/values-dapr.yaml --wait

# 5. Access
minikube service todo-chatbot-frontend --url
```

### Verification

```bash
# Test Pub/Sub
kubectl exec deploy/todo-chatbot-backend -c todo-backend -- \
  curl -s -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"specversion":"1.0","type":"com.todo.task.test","source":"/test","id":"t1","data":{"test":true}}'

# Consume from Kafka
kubectl exec deploy/redpanda -- rpk topic consume task-events -n 1 --brokers localhost:9092
```

### Documentation

- **Deployment Guide**: `DEPLOYMENT.md`
- **Dapr Components**: `docs/dapr-components.md`
- **Troubleshooting**: `docs/troubleshooting.md`
- **Spec**: `specs/006-phase5-partb-local-deployment/spec.md`

## Part C: Cloud Deployment on Oracle OKE (Always Free)

**Cost: $0.00** | Oracle Cloud Always Free + Redpanda Cloud Free Tier

Phase V Part C deploys the complete application to Oracle Cloud Infrastructure (OCI) Kubernetes Engine (OKE) with zero cost.

### Cloud Architecture

```
ORACLE OKE CLUSTER (Always Free, ARM64 Ampere A1)
├── dapr-system (operator, sidecar-injector, placement, sentry)
├── default namespace
│   ├── todo-backend    [FastAPI + Dapr sidecar]     2/2
│   ├── todo-frontend   [Next.js + Dapr sidecar]     2/2
│   └── Dapr Components: kafka-pubsub (SASL), statestore, kubernetes-secrets
├── LoadBalancer Service → Public IP (frontend)
└── External Services:
    ├── Redpanda Cloud (Kafka, serverless free tier)
    ├── Neon PostgreSQL (free tier)
    └── GitHub Actions CI/CD → ghcr.io images
```

### Key Features

- **Oracle OKE Always Free**: 4 OCPUs, 24GB RAM (ARM64 Ampere A1)
- **Redpanda Cloud Kafka**: SASL/SCRAM-SHA-256 authenticated, serverless
- **Multi-arch Docker images**: ARM64 + AMD64 via Docker buildx
- **GitHub Actions CI/CD**: Auto build/push/deploy on push to main/deploy
- **Public LoadBalancer**: Frontend accessible via external IP
- **$0 cost**: All services within free tier limits

### Quick Deploy

```bash
# Prerequisites: OKE cluster + kubectl + Dapr + K8s secrets created
cd phase5/

# Deploy with cloud values
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values.yaml \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  --set kafka.brokerUrl="<REDPANDA_URL>:9092" \
  --set secrets.databaseUrl="<NEON_URL>" \
  --set secrets.cohereApiKey="<COHERE_KEY>" \
  --set secrets.jwtSecret="<JWT_SECRET>"

# Get public URL
kubectl get svc todo-chatbot-frontend
```

### Documentation

- **Full Cloud Guide**: [docs/CLOUD-DEPLOYMENT.md](docs/CLOUD-DEPLOYMENT.md)
- **Quickstart**: [specs/007-phase5-partc-cloud-deployment/quickstart.md](specs/007-phase5-partc-cloud-deployment/quickstart.md)
- **Spec**: [specs/007-phase5-partc-cloud-deployment/spec.md](specs/007-phase5-partc-cloud-deployment/spec.md)
- **CI/CD Workflow**: [.github/workflows/deploy-cloud.yml](../.github/workflows/deploy-cloud.yml)
