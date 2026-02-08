# Implementation Plan: Phase V Part B - Local Minikube + Dapr + Kafka

**Feature ID**: 006-phase5-partb-local-deployment
**Version**: 1.0.0
**Created**: 2026-02-04
**Author**: Claude Code Agent

---

## 1. Technical Context

### 1.1 Current State

| Component | Status | Location |
|-----------|--------|----------|
| Phase V Part A Code | Complete | `phase5/backend/`, `phase5/frontend/` |
| Phase IV Helm Charts | Available | `phase4_chatbot/helm/todo-chatbot/` |
| Dapr CLI | Required | User's local machine |
| Minikube | Required | User's local machine |
| Docker | Required | Docker Desktop running |

### 1.2 Target State

| Component | Target | Verification |
|-----------|--------|--------------|
| Minikube Cluster | Running (4GB, 2CPU) | `minikube status` |
| Dapr Runtime | Initialized | `dapr status -k` |
| Redpanda (Kafka) | Running | `kubectl get pods -l app=redpanda` |
| Application Pods | 2/2 containers (sidecar) | `kubectl get pods` |
| Event Flow | Task → Kafka | `rpk topic consume` |

### 1.3 Technology Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| Minikube | 1.30+ | Local Kubernetes |
| Dapr | 1.12+ | Distributed runtime |
| Redpanda | Latest | Kafka-compatible broker |
| Helm | 3.x | Deployment management |
| kubectl-ai | Latest | AI-assisted K8s operations |
| kagent | Latest | AI-assisted K8s operations |

---

## 2. Constitution Check

### 2.1 Principle Compliance

| Principle | Plan Alignment | Status |
|-----------|----------------|--------|
| P1: Spec-Driven | All tasks reference spec sections | ✓ COMPLIANT |
| P2: AI-Assisted Infrastructure | kubectl-ai/kagent for all ops | ✓ COMPLIANT |
| P3: Backward Compatibility | Phase III/IV/V-A preserved | ✓ COMPLIANT |
| P4: Full Dapr Runtime | All 5 building blocks | ✓ COMPLIANT |
| P5: Dapr-Exclusive | No direct Kafka client | ✓ COMPLIANT |
| P6: Local Kafka | Redpanda chosen | ✓ COMPLIANT |
| P7: Extend Phase IV Helm | Building on existing charts | ✓ COMPLIANT |

### 2.2 Non-Negotiable Gates

| Non-Negotiable | Enforcement | Status |
|----------------|-------------|--------|
| No Dapr bypass | All events via Dapr Pub/Sub | ✓ GATE PASS |
| No direct Kafka | EventPublisher uses Dapr HTTP | ✓ GATE PASS |
| No Phase breakage | Test suite validation | ✓ GATE PASS |
| No manual kubectl | Agent-only operations | ✓ GATE PASS |
| No cloud credentials | Local-only deployment | ✓ GATE PASS |
| No consumers yet | Publish + verify only | ✓ GATE PASS |

---

## 3. Architecture Sketch

```
Local Machine (Docker Desktop)
└── Minikube Cluster
    ├── Namespace: dapr-system
    │   ├── dapr-operator
    │   ├── dapr-sidecar-injector
    │   ├── dapr-placement
    │   └── dapr-sentry
    │
    ├── Namespace: default
    │   ├── Pod: todo-frontend (Next.js + ChatKit)
    │   │   ├── Container: frontend (port 3000)
    │   │   └── Container: daprd (sidecar, port 3500)
    │   │
    │   ├── Pod: todo-backend (FastAPI + Cohere + MCP)
    │   │   ├── Container: backend (port 8000)
    │   │   └── Container: daprd (sidecar, port 3500)
    │   │
    │   ├── Pod: redpanda-kafka
    │   │   └── Container: redpanda (port 9092)
    │   │
    │   └── Dapr Components:
    │       ├── kafka-pubsub (pubsub.kafka)
    │       ├── statestore (state.postgresql)
    │       └── kubernetes-secrets (secretstores.kubernetes)
    │
    └── External
        └── Neon PostgreSQL (main DB)
```

---

## 4. Key Decisions & Tradeoffs

| Decision | Chosen Option | Alternatives | Rationale |
|----------|---------------|--------------|-----------|
| Kafka Broker | Redpanda single pod | Strimzi operator | Simpler, no Zookeeper, fast startup |
| Dapr Install | `dapr init -k` | Manual YAML | Official method, automatic injection |
| Sidecar Injection | Helm annotations | dapr.yaml in pod spec | Cleaner, Helm-native approach |
| Topic Creation | Auto-create (Dapr) | Manual `kafka-topics.sh` | Less manual work |
| State Store | Dapr state.postgresql (Neon) | Dapr state.redis | Consistent with existing DB |
| Secrets | Kubernetes Secrets + Dapr | Vault, Sealed Secrets | Simpler for local dev |

---

## 5. Implementation Phases

### Phase 1: Environment Verification & Dapr Installation

| Task | Agent | Description |
|------|-------|-------------|
| T601 | K8sAgent | Verify Minikube running with sufficient resources |
| T602 | K8sAgent | Enable required Minikube addons (ingress, metrics-server) |
| T603 | K8sAgent | Install Dapr on Minikube (`dapr init -k --wait`) |
| T604 | K8sAgent | Verify Dapr system pods healthy |

**Gate**: `dapr status -k` shows all components healthy

### Phase 2: Kafka (Redpanda) Deployment

| Task | Agent | Description |
|------|-------|-------------|
| T605 | HelmAgent | Create Redpanda deployment template |
| T606 | HelmAgent | Create Redpanda service template |
| T607 | K8sAgent | Deploy Redpanda pod |
| T608 | KafkaAgent | Verify Redpanda healthy and accessible |
| T609 | KafkaAgent | Create topics (task-events, reminders) |

**Gate**: `rpk topic list` shows topics

### Phase 3: Helm Chart Extension for Dapr

| Task | Agent | Description |
|------|-------|-------------|
| T610 | HelmAgent | Copy Phase IV Helm chart to Phase 5 |
| T611 | HelmAgent | Add Dapr annotations to backend deployment |
| T612 | HelmAgent | Add Dapr annotations to frontend deployment |
| T613 | HelmAgent | Create values-dapr.yaml with Dapr configuration |
| T614 | HelmAgent | Update Chart.yaml with Part B version |

**Gate**: `helm lint` passes

### Phase 4: Dapr Components Configuration

| Task | Agent | Description |
|------|-------|-------------|
| T615 | DaprAgent | Create kafka-pubsub component template |
| T616 | DaprAgent | Create statestore component template |
| T617 | DaprAgent | Create kubernetes-secrets component template |
| T618 | HelmAgent | Add Dapr components to Helm templates |
| T619 | K8sAgent | Create Kubernetes secrets for API keys |

**Gate**: Components visible in `kubectl get components.dapr.io`

### Phase 5: Application Deployment

| Task | Agent | Description |
|------|-------|-------------|
| T620 | K8sAgent | Build and load backend Docker image to Minikube |
| T621 | K8sAgent | Build and load frontend Docker image to Minikube |
| T622 | K8sAgent | Helm install todo-app with Dapr values |
| T623 | K8sAgent | Verify pods have 2/2 containers (sidecar injected) |
| T624 | K8sAgent | Verify services created and accessible |

**Gate**: All pods Running with 2/2 containers

### Phase 6: Event Integration Verification

| Task | Agent | Description |
|------|-------|-------------|
| T625 | KafkaAgent | Test manual publish via Dapr sidecar |
| T626 | KafkaAgent | Verify message in task-events topic |
| T627 | K8sAgent | Test task creation via application |
| T628 | KafkaAgent | Verify CloudEvents schema in messages |
| T629 | K8sAgent | Verify Dapr sidecar logs show publish calls |

**Gate**: Events visible in Kafka with CloudEvents format

### Phase 7: Dapr Building Blocks Testing

| Task | Agent | Description |
|------|-------|-------------|
| T630 | DaprAgent | Test Pub/Sub: publish/verify |
| T631 | DaprAgent | Test State Store: save/retrieve |
| T632 | DaprAgent | Test Secrets: get API key |
| T633 | DaprAgent | Test Jobs API: schedule/callback |
| T634 | DaprAgent | Test Service Invocation: frontend→backend |

**Gate**: All 5 building blocks functional

### Phase 8: End-to-End Application Testing

| Task | Agent | Description |
|------|-------|-------------|
| T635 | OrchestratorAgent | Access frontend via minikube service |
| T636 | OrchestratorAgent | Test login flow |
| T637 | OrchestratorAgent | Test chatbot with all Phase V Part A features |
| T638 | OrchestratorAgent | Verify event publishing on task operations |
| T639 | OrchestratorAgent | Verify user isolation maintained |

**Gate**: Full application functional in Minikube

### Phase 9: Documentation & Cleanup

| Task | Agent | Description |
|------|-------|-------------|
| T640 | OrchestratorAgent | Create deployment README with exact commands |
| T641 | OrchestratorAgent | Document Helm values configuration |
| T642 | OrchestratorAgent | Document Dapr component YAMLs |
| T643 | OrchestratorAgent | Create troubleshooting guide |
| T644 | OrchestratorAgent | Create architecture diagram |
| T645 | OrchestratorAgent | Update project README with Part B section |

**Gate**: Documentation complete and reproducible

---

## 6. Testing/Validation Strategy

### 6.1 Infrastructure Tests

| Check | Command | Expected |
|-------|---------|----------|
| Minikube running | `minikube status` | Running |
| Dapr initialized | `dapr status -k` | All healthy |
| Sidecars running | `kubectl get pods` | 2/2 containers |
| Kafka healthy | `kubectl logs redpanda-0` | No errors |

### 6.2 Dapr Component Tests

| Building Block | Test Method | Expected |
|----------------|-------------|----------|
| Pub/Sub | POST to sidecar:3500/publish | 204 + message in topic |
| State Store | POST/GET to sidecar:3500/state | Data persisted |
| Secrets | GET sidecar:3500/secrets | Key value returned |
| Jobs | POST to sidecar:3500/jobs | Callback received |
| Service Invocation | GET sidecar:3500/invoke | Response from target |

### 6.3 Application Tests

| Feature | Test Method | Expected |
|---------|-------------|----------|
| Login | UI interaction | Dashboard displayed |
| Task CRUD | Chatbot commands | Task + event |
| Priority | "add high priority task X" | Priority set |
| Tags | "add task X #work" | Tag applied |
| Recurring | "add daily task X" | Recurrence created |
| Search | "search tasks for X" | Results filtered |

---

## 7. Helm Chart Structure (Extended)

```
phase5/helm/todo-chatbot/
├── Chart.yaml                    # Updated version
├── values.yaml                   # Base values
├── values-dapr.yaml              # NEW: Dapr-specific values
├── templates/
│   ├── _helpers.tpl              # From Phase IV
│   ├── backend-deployment.yaml   # UPDATED: Dapr annotations
│   ├── backend-service.yaml      # From Phase IV
│   ├── frontend-deployment.yaml  # UPDATED: Dapr annotations
│   ├── frontend-service.yaml     # From Phase IV
│   ├── configmap.yaml            # From Phase IV
│   ├── secret.yaml               # UPDATED: API keys
│   ├── NOTES.txt                 # UPDATED: Dapr info
│   ├── dapr/                     # NEW DIRECTORY
│   │   ├── pubsub-kafka.yaml     # kafka-pubsub component
│   │   ├── statestore.yaml       # state.postgresql component
│   │   └── secretstore.yaml      # kubernetes secrets component
│   └── kafka/                    # NEW DIRECTORY
│       ├── redpanda-deployment.yaml
│       └── redpanda-service.yaml
```

---

## 8. Agent Responsibilities

| Agent | Responsibility | Tools Used |
|-------|----------------|------------|
| K8sAgent | Cluster operations, pod management | kubectl-ai, minikube |
| HelmAgent | Chart creation, template updates | helm, kubectl-ai |
| DaprAgent | Component config, building block tests | dapr CLI, curl |
| KafkaAgent | Broker management, topic operations | rpk, kubectl-ai |
| OrchestratorAgent | E2E tests, documentation | all tools |

---

## 9. Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Resource constraints | Pods fail to start | Optimize limits (512Mi backend, 256Mi frontend) |
| Sidecar injection fails | No event publishing | Verify namespace labels, restart pods |
| Kafka connectivity | Events not flowing | Check broker address, component config |
| Secret access denied | Auth failures | Verify RBAC, secret names |
| Image pull errors | Pods pending | Use `minikube image load` |

---

## 10. Success Criteria Mapping

| Spec SC | Plan Phase | Tasks | Verification |
|---------|------------|-------|--------------|
| SC-001 | Phase 1 | T601-T604 | `dapr status -k` |
| SC-002 | Phase 2 | T605-T609 | `rpk topic list` |
| SC-003 | Phase 5 | T620-T624 | 2/2 containers |
| SC-004 | Phase 6 | T625-T629 | Events in Kafka |
| SC-005 | Phase 7 | T630-T634 | All blocks pass |
| SC-006 | Phase 8 | T635-T639 | Full app works |
| SC-007 | Phase 9 | T640-T645 | Docs complete |

---

## 11. Appendix: Dapr Component Examples

### A. kafka-pubsub.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "redpanda.default.svc.cluster.local:9092"
    - name: consumerGroup
      value: "todo-app"
    - name: authRequired
      value: "false"
scopes:
  - todo-backend
```

### B. statestore.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
  namespace: default
spec:
  type: state.postgresql
  version: v1
  metadata:
    - name: connectionString
      secretKeyRef:
        name: db-secrets
        key: connection-string
scopes:
  - todo-backend
```

### C. secretstore.yaml

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
  namespace: default
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

---

## 12. Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-02-04 | Initial implementation plan |
