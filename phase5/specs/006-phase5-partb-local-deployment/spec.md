# Feature Specification: Phase V Part B - Local Minikube + Dapr + Kafka Deployment

**Feature ID**: 006-phase5-partb-local-deployment
**Version**: 1.0.0
**Status**: Draft
**Created**: 2026-02-03
**Author**: Claude Code Agent

---

## 1. Overview

### 1.1 Summary

Deploy the Phase V application (with Part A advanced features and Dapr event publishing code) on a local Minikube cluster with full Dapr runtime and local Kafka (Redpanda) to validate event-driven architecture before cloud deployment.

### 1.2 Problem Statement

Phase V Part A implemented event publishing code patterns but without actual infrastructure. Part B provides the local runtime environment to:
- Validate Dapr Pub/Sub integration with real Kafka
- Test all 5 Dapr building blocks in a Kubernetes context
- Prove the application works in a containerized, sidecar-injected environment
- Create a reusable blueprint for cloud deployment in Part C

### 1.3 Goals

1. Deploy complete application stack on Minikube with Dapr sidecars
2. Run local Kafka (Redpanda) for event streaming
3. Verify end-to-end event flows from task operations to Kafka topics
4. Test Dapr Jobs API for reminder scheduling
5. Document deployment for reproducibility

### 1.4 Non-Goals (Out of Scope)

- Cloud deployment (Part C)
- Consumer services (recurring engine, notifications)
- Real-time WebSocket synchronization
- Production-grade high availability
- Kafka consumer pod deployment

---

## 2. User Stories

### US-001: Developer Deploys Application Stack

**As a** developer
**I want to** deploy the todo application with Dapr to Minikube
**So that** I can test event-driven features locally

**Acceptance Criteria**:
- [ ] `helm install` command succeeds without errors
- [ ] All pods reach Running state within 5 minutes
- [ ] Dapr sidecars injected on frontend and backend pods
- [ ] `kubectl get pods` shows 2/2 containers for app pods (app + sidecar)

### US-002: Developer Verifies Kafka Integration

**As a** developer
**I want to** see task events flowing to Kafka topics
**So that** I can confirm the event-driven architecture works

**Acceptance Criteria**:
- [ ] Redpanda/Kafka pod running and healthy
- [ ] Topics `task-events` and `reminders` exist
- [ ] Creating a task via UI/chatbot produces event in `task-events` topic
- [ ] Event follows CloudEvents 1.0 schema
- [ ] `rpk topic consume` shows the message

### US-003: Developer Tests Dapr Pub/Sub

**As a** developer
**I want to** verify Dapr Pub/Sub component is configured correctly
**So that** the backend can publish events through Dapr sidecar

**Acceptance Criteria**:
- [ ] `kafka-pubsub` component deployed via Helm
- [ ] Backend sidecar logs show successful publish calls
- [ ] Manual publish test via curl to `localhost:3500` succeeds
- [ ] Component scoped to backend app-id

### US-004: Developer Tests Dapr Jobs API

**As a** developer
**I want to** schedule a reminder job via Dapr Jobs API
**So that** I can verify scheduled callbacks work

**Acceptance Criteria**:
- [ ] Can schedule job via POST to `/v1.0/jobs/{name}`
- [ ] Job triggers callback endpoint at scheduled time
- [ ] Can list jobs via GET `/v1.0/jobs`
- [ ] Can delete job via DELETE `/v1.0/jobs/{name}`

### US-005: Developer Tests Dapr State Store

**As a** developer
**I want to** use Dapr state store for conversation caching
**So that** I can validate state management building block

**Acceptance Criteria**:
- [ ] `statestore` component configured with PostgreSQL
- [ ] Can save state via POST to `/v1.0/state/statestore`
- [ ] Can retrieve state via GET `/v1.0/state/statestore/{key}`
- [ ] State persists across pod restarts

### US-006: Developer Tests Dapr Secrets

**As a** developer
**I want to** access secrets via Dapr secrets API
**So that** sensitive configuration is managed securely

**Acceptance Criteria**:
- [ ] Kubernetes secrets created for API keys
- [ ] `kubernetes-secrets` component deployed
- [ ] Backend can retrieve COHERE_API_KEY via Dapr
- [ ] Secrets not exposed in pod environment variables

### US-007: Developer Uses Full Application

**As a** developer
**I want to** use the complete application in Minikube
**So that** I can verify all Phase V Part A features work in K8s

**Acceptance Criteria**:
- [ ] Access frontend via `minikube service`
- [ ] Can login and see dashboard
- [ ] Chatbot responds to all commands (priorities, tags, recurring, etc.)
- [ ] All Part A features functional
- [ ] User isolation maintained

### US-008: Developer Documents Deployment

**As a** developer
**I want to** have complete deployment documentation
**So that** the setup is reproducible and explainable

**Acceptance Criteria**:
- [ ] README with exact commands
- [ ] Helm values documented
- [ ] Dapr component YAMLs explained
- [ ] Troubleshooting guide included
- [ ] Architecture diagram provided

---

## 3. Functional Requirements

### FR-001: Minikube Cluster Setup

The deployment MUST support a Minikube cluster with:
- Minimum 4GB memory, 2 CPUs
- Docker driver (preferred)
- Ingress addon enabled
- Metrics server addon enabled

### FR-002: Dapr Runtime Installation

Dapr MUST be installed with:
- `dapr init -k` command
- All system components healthy
- Sidecar injection enabled for default namespace

### FR-003: Kafka/Redpanda Deployment

Local Kafka MUST be deployed with:
- Redpanda single-container (recommended) or Strimzi operator
- Broker accessible at port 9092
- Topics auto-created by Dapr or manually created

### FR-004: Helm Chart Extensions

Phase IV Helm charts MUST be extended with:
- Dapr sidecar annotations on all deployments
- Dapr component manifests (pubsub, state, secrets)
- Redpanda deployment template
- Configurable via values.yaml

### FR-005: Event Flow Validation

The system MUST support validation of:
- Task CRUD → Kafka event publishing
- CloudEvents schema compliance
- Dapr sidecar logging
- Kafka topic consumption for verification

---

## 4. Technical Architecture

### 4.1 Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         MINIKUBE CLUSTER                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     DAPR SYSTEM (dapr-system ns)             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │    │
│  │  │   Operator  │  │  Sidecar    │  │  Placement/Sentry   │  │    │
│  │  │             │  │  Injector   │  │                     │  │    │
│  │  └─────────────┘  └─────────────┘  └─────────────────────┘  │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                     APPLICATION (default ns)                 │    │
│  │                                                              │    │
│  │  ┌─────────────────────┐    ┌─────────────────────┐         │    │
│  │  │   todo-frontend     │    │    todo-backend     │         │    │
│  │  │  ┌──────┬───────┐   │    │  ┌──────┬───────┐   │         │    │
│  │  │  │ Next │ Dapr  │   │    │  │ Fast │ Dapr  │   │         │    │
│  │  │  │ .js  │Sidecar│   │    │  │ API  │Sidecar│   │         │    │
│  │  │  │:3000 │ :3500 │   │    │  │:8000 │ :3500 │   │         │    │
│  │  │  └──────┴───────┘   │    │  └──────┴───────┘   │         │    │
│  │  └─────────────────────┘    └──────────┬──────────┘         │    │
│  │                                        │                     │    │
│  │                              ┌─────────▼─────────┐           │    │
│  │                              │    Dapr Pub/Sub   │           │    │
│  │                              │   (kafka-pubsub)  │           │    │
│  │                              └─────────┬─────────┘           │    │
│  │                                        │                     │    │
│  │  ┌─────────────────────────────────────▼───────────────────┐│    │
│  │  │                      REDPANDA                           ││    │
│  │  │  ┌─────────────────┐  ┌─────────────────┐              ││    │
│  │  │  │  task-events    │  │   reminders     │              ││    │
│  │  │  │     topic       │  │     topic       │              ││    │
│  │  │  └─────────────────┘  └─────────────────┘              ││    │
│  │  └─────────────────────────────────────────────────────────┘│    │
│  └─────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────┐     │
│  │                    DAPR COMPONENTS                          │     │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐    │     │
│  │  │ kafka-pubsub │ │  statestore  │ │ kubernetes-secrets│    │     │
│  │  │ (pubsub.kafka│ │(state.postgres│ │(secretstores.k8s)│    │     │
│  │  └──────────────┘ └──────────────┘ └──────────────────┘    │     │
│  └────────────────────────────────────────────────────────────┘     │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ External
                                   ▼
                    ┌──────────────────────────┐
                    │      NEON PostgreSQL     │
                    │    (External Database)   │
                    └──────────────────────────┘
```

### 4.2 Component Specifications

#### 4.2.1 Dapr Components

| Component | Type | Purpose | Configuration |
|-----------|------|---------|---------------|
| kafka-pubsub | pubsub.kafka | Event streaming | brokers: redpanda:9092 |
| statestore | state.postgresql | Session cache | Neon connection string |
| kubernetes-secrets | secretstores.kubernetes | API keys | Namespace: default |

#### 4.2.2 Kafka Topics

| Topic | Purpose | Events |
|-------|---------|--------|
| task-events | Task lifecycle | created, updated, completed, deleted |
| reminders | Scheduling | reminder.due, recurring.triggered |

#### 4.2.3 Pod Annotations

```yaml
metadata:
  annotations:
    dapr.io/enabled: "true"
    dapr.io/app-id: "<app-name>"
    dapr.io/app-port: "<port>"
    dapr.io/log-level: "info"
    dapr.io/enable-api-logging: "true"
```

### 4.3 Helm Chart Structure

```
helm/todo-app/
├── Chart.yaml
├── values.yaml
├── values-dapr.yaml          # Part B additions
├── templates/
│   ├── backend-deployment.yaml   # Extended with Dapr
│   ├── frontend-deployment.yaml  # Extended with Dapr
│   ├── backend-service.yaml
│   ├── frontend-service.yaml
│   ├── configmap.yaml
│   ├── secrets.yaml
│   ├── dapr/                     # NEW for Part B
│   │   ├── pubsub-kafka.yaml
│   │   ├── statestore.yaml
│   │   └── secretstore.yaml
│   └── kafka/                    # NEW for Part B
│       └── redpanda.yaml
```

---

## 5. Dapr Building Blocks Usage

### 5.1 Pub/Sub (pubsub.kafka)

**Purpose**: Event streaming for task lifecycle events

**Usage Pattern**:
```python
# Backend publishes via HTTP to Dapr sidecar
POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events
Content-Type: application/cloudevents+json
```

**Verification**:
```bash
# Consume from Kafka topic
kubectl exec redpanda-0 -- rpk topic consume task-events -n 1
```

### 5.2 State Store (state.postgresql)

**Purpose**: Conversation session caching

**Usage Pattern**:
```python
# Save state
POST http://localhost:3500/v1.0/state/statestore
[{"key": "session-123", "value": {"messages": [...]}}]

# Get state
GET http://localhost:3500/v1.0/state/statestore/session-123
```

### 5.3 Secrets (secretstores.kubernetes)

**Purpose**: Secure API key access

**Usage Pattern**:
```python
# Get secret
GET http://localhost:3500/v1.0/secrets/kubernetes-secrets/cohere-api-key
```

### 5.4 Jobs API

**Purpose**: Reminder scheduling

**Usage Pattern**:
```python
# Schedule job
POST http://localhost:3500/v1.0/jobs/reminder-task-123
{
  "schedule": "@every 1h",
  "callback": {"method": "POST", "path": "/api/reminders/callback"}
}

# List jobs
GET http://localhost:3500/v1.0/jobs

# Delete job
DELETE http://localhost:3500/v1.0/jobs/reminder-task-123
```

### 5.5 Service Invocation

**Purpose**: Service-to-service communication

**Usage Pattern**:
```python
# Frontend calls backend via Dapr
GET http://localhost:3500/v1.0/invoke/todo-backend/method/api/health
```

---

## 6. Success Criteria

### SC-001: Cluster Health

| Check | Command | Expected |
|-------|---------|----------|
| Minikube running | `minikube status` | Running |
| Dapr healthy | `dapr status -k` | All components healthy |
| Pods running | `kubectl get pods` | All Running, 2/2 containers |

### SC-002: Kafka Integration

| Check | Command | Expected |
|-------|---------|----------|
| Redpanda running | `kubectl get pods -l app=redpanda` | Running |
| Topics exist | `rpk topic list` | task-events, reminders |
| Pub/Sub test | Manual publish via curl | 204 response |
| Message visible | `rpk topic consume` | CloudEvents JSON |

### SC-003: Event Flow

| Check | Method | Expected |
|-------|--------|----------|
| Create task | Chatbot command | Event in task-events topic |
| Update task | API call | Event in task-events topic |
| Complete task | Chatbot command | Event + recurring trigger if applicable |

### SC-004: Dapr Building Blocks

| Building Block | Test | Expected |
|----------------|------|----------|
| Pub/Sub | Publish event | Message in Kafka |
| State | Save/retrieve | Data persisted |
| Secrets | Get API key | Key value returned |
| Jobs | Schedule/callback | Callback received |
| Service Invocation | Cross-service call | Response received |

### SC-005: Application Functionality

| Check | Method | Expected |
|-------|--------|----------|
| Frontend access | `minikube service` | Login page loads |
| Dashboard | Navigate | Tasks displayed |
| Chatbot | Send command | Response received |
| Part A features | Test all | All working |

---

## 7. Constraints

| Constraint | Description | Rationale |
|------------|-------------|-----------|
| Local only | Minikube, no cloud | Part B scope |
| Neon DB external | Main storage unchanged | Continuity |
| Redpanda preferred | Single container | Simplicity |
| No consumers | Publish only | Part B scope |
| AI agents only | kubectl-ai, kagent | Hackathon requirement |
| Resource limits | 4GB/2CPU minimum | Laptop-friendly |

---

## 8. Dependencies

### 8.1 Prerequisites

- Phase V Part A code complete and working
- Phase IV Helm charts available
- Minikube installed locally
- Docker daemon running
- Dapr CLI installed

### 8.2 External Services

- Neon PostgreSQL (existing)
- No cloud services in Part B

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Resource constraints | Pods fail to start | Optimize limits, use Redpanda |
| Dapr sidecar injection fails | No event publishing | Verify namespace labels, restart pods |
| Kafka connectivity | Events not flowing | Check broker address, component config |
| Secret access denied | App can't authenticate | Verify RBAC, secret names |

---

## 10. Glossary

| Term | Definition |
|------|------------|
| Dapr | Distributed Application Runtime |
| Sidecar | Container running alongside app container |
| Pub/Sub | Publish/Subscribe messaging pattern |
| Redpanda | Kafka-compatible streaming platform |
| Strimzi | Kubernetes operator for Apache Kafka |
| CloudEvents | Specification for event data format |
| rpk | Redpanda CLI tool |

---

## 11. References

- [Dapr Documentation](https://docs.dapr.io)
- [Redpanda Documentation](https://docs.redpanda.com)
- [Strimzi Documentation](https://strimzi.io/docs)
- [Phase V Part A Spec](../005-phase5-parta-advanced-events/spec.md)
- [Phase IV K8s Spec](../004-local-k8s-deployment/spec.md)
- [Constitution v4.0.0](../../.specify/memory/constitution.md)
