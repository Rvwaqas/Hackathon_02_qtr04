---
id: 001
title: Phase V Part B Specification
stage: spec
date: 2026-02-04
surface: agent
model: claude-opus-4-5-20251101
feature: 006-phase5-partb-local-deployment
branch: 1-phase5-parta-advanced-events
user: waqas
command: /sp.specify
labels: ["specification", "phase5", "partb", "minikube", "dapr", "kafka", "redpanda", "helm", "kubernetes"]
links:
  spec: specs/006-phase5-partb-local-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-phase5-partb-local-deployment/spec.md
  - specs/006-phase5-partb-local-deployment/contracts/dapr-components.yaml
  - specs/006-phase5-partb-local-deployment/contracts/helm-values-schema.yaml
  - specs/006-phase5-partb-local-deployment/contracts/cloudevents-schema.json
  - specs/006-phase5-partb-local-deployment/checklists/deployment-checklist.md
tests:
  - null
---

## Prompt

```text
/sp.specify
# speckit.spec - Hackathon II: Evolution of Todo (Phase V - Part B: Local Minikube + Dapr + Kafka)

## Project
Phase V – Part B: Deploy the extended Phase V application (with advanced features and Dapr event publishing code) on local Minikube with full Dapr and local Kafka (Redpanda/Strimzi)

## Specification Outline

### User Journeys (Post-Deployment Testing)
1. Helm Install: `helm install todo-app ./helm/todo-app -f values-dapr.yaml`
2. Verify Pods: 2/2 containers (app + Dapr sidecar)
3. Verify Kafka: Redpanda running, topics exist
4. Test Event Flow: Create task → Check Kafka topic
5. Test Dapr Jobs: Schedule reminder → Verify callback
6. Use Application: Access via minikube service, test chatbot

### Success Criteria
- SC-001: Minikube + Dapr all healthy
- SC-002: Kafka/Redpanda pods running
- SC-003: Helm deploy with Dapr sidecars (2/2 containers)
- SC-004: Task events visible in Kafka topics
- SC-005: Dapr Jobs API working
- SC-006: Application fully functional
- SC-007: Documentation complete

### Constraints
- Local Minikube only (no cloud)
- Neon DB external (unchanged)
- Redpanda or Strimzi for local Kafka
- Dapr Jobs API for reminders (not cron)
- No consumer pods yet (publish + verify only)

### Out of Scope (Part C)
- Cloud deployment (Part C)
- Consumer services
- Real-time sync
- Production HA
```

## Response snapshot

### Feature Specification Created

Successfully created comprehensive specification for Phase V Part B - Local Minikube + Dapr + Kafka Deployment.

**Specification File**: `specs/006-phase5-partb-local-deployment/spec.md`

### User Stories Defined

| ID | Story | Focus |
|----|-------|-------|
| US-001 | Developer Deploys Application Stack | Helm install, pod verification |
| US-002 | Developer Verifies Kafka Integration | Redpanda, topics, event flow |
| US-003 | Developer Tests Dapr Pub/Sub | kafka-pubsub component |
| US-004 | Developer Tests Dapr Jobs API | Reminder scheduling |
| US-005 | Developer Tests Dapr State Store | Conversation caching |
| US-006 | Developer Tests Dapr Secrets | Secure API key access |
| US-007 | Developer Uses Full Application | End-to-end verification |
| US-008 | Developer Documents Deployment | Reproducibility |

### Technical Architecture

Created architecture diagram showing:
- Minikube cluster with Dapr system namespace
- Application pods with Dapr sidecars (2/2 containers)
- Redpanda for Kafka (task-events, reminders topics)
- Dapr components: kafka-pubsub, statestore, kubernetes-secrets
- External Neon PostgreSQL connection

### Dapr Building Blocks

Documented all 5 building blocks with usage patterns:
1. **Pub/Sub** (pubsub.kafka) - Task event streaming
2. **State Store** (state.postgresql) - Conversation caching
3. **Secrets** (secretstores.kubernetes) - API key access
4. **Jobs API** - Reminder scheduling
5. **Service Invocation** - Service-to-service communication

### Contracts Created

| File | Purpose |
|------|---------|
| `contracts/dapr-components.yaml` | Dapr component manifests |
| `contracts/helm-values-schema.yaml` | Helm values JSON schema |
| `contracts/cloudevents-schema.json` | CloudEvents 1.0 event schema |

### Checklists Created

| File | Purpose |
|------|---------|
| `checklists/deployment-checklist.md` | Full deployment verification |

### Success Criteria

| ID | Criterion | Verification |
|----|-----------|--------------|
| SC-001 | Cluster Health | `minikube status`, `dapr status -k` |
| SC-002 | Kafka Integration | `rpk topic list`, consume test |
| SC-003 | Event Flow | Task CRUD → Kafka events |
| SC-004 | Dapr Building Blocks | All 5 blocks functional |
| SC-005 | Application Functionality | Full feature test |

## Outcome

- Impact: Complete specification for Phase V Part B local deployment
- Tests: N/A - specification document
- Files: 5 files created (spec.md + 3 contracts + 1 checklist)
- Next prompts: `/sp.plan` for implementation plan, `/sp.tasks` for task breakdown
- Reflection: Comprehensive specification with clear acceptance criteria and verification procedures

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
  - User stories with acceptance criteria: ✓ (8 stories)
  - Architecture diagram: ✓
  - Dapr building blocks documented: ✓ (all 5)
  - Contracts defined: ✓ (3 files)
  - Success criteria measurable: ✓ (5 criteria with commands)
  - Helm chart structure defined: ✓
  - Constraints documented: ✓
  - Dependencies listed: ✓
- Prompt variant (if applicable): N/A
- Next experiment: Create implementation plan with AI-agent-focused tasks
