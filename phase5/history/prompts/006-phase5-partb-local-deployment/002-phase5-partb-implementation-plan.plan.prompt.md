---
id: 002
title: Phase V Part B Implementation Plan
stage: plan
date: 2026-02-04
surface: agent
model: claude-opus-4-5-20251101
feature: 006-phase5-partb-local-deployment
branch: 1-phase5-parta-advanced-events
user: waqas
command: /sp.plan
labels: ["plan", "phase5", "partb", "minikube", "dapr", "kafka", "helm", "kubernetes", "infrastructure"]
links:
  spec: specs/006-phase5-partb-local-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/006-phase5-partb-local-deployment/plan.md
  - specs/006-phase5-partb-local-deployment/research.md
  - specs/006-phase5-partb-local-deployment/data-model.md
  - specs/006-phase5-partb-local-deployment/quickstart.md
tests:
  - null
---

## Prompt

```text
/sp.plan
# specs/plan.md - Hackathon II: Phase V - Part B: Local Minikube + Dapr + Kafka

## Architecture Sketch (Part B – Local Deployment Level)
Extended Phase IV Minikube setup with Dapr sidecars and local Kafka.
Local Machine (Docker Desktop)
└── Minikube Cluster
├── Pod: todo-frontend (Next.js + ChatKit)
│   └── Dapr Sidecar (injected)
├── Pod: todo-backend (FastAPI + Cohere + MCP)
│   └── Dapr Sidecar (injected)
├── Pod: redpanda-kafka (single container or Strimzi broker)
├── Dapr Components (ConfigMap/Secret):
│   ├── pubsub.kafka → connects to Redpanda
│   ├── state.postgresql → Neon DB for cache
│   ├── jobs → scheduled reminders
│   ├── secrets.kubernetes → COHERE_API_KEY, etc.
└── External → Neon PostgreSQL (main DB)

## Component Breakdown
### Helm Chart Extension (/helm/todo-chatbot/)
- values.yaml: dapr.enabled=true, kafka.enabled=true
- templates: dapr-sidecar annotations, Kafka pod, dapr-components.yaml

### Dapr Components
- pubsub.kafka: brokers = kafka:9092
- state.postgresql: connectionString = Neon URL
- jobs: for reminder scheduling
- secrets.kubernetes: for API keys

### Kafka Setup
- Redpanda: single pod with docker.io/redpandadata/redpanda
- Strimzi (alternative): Kafka CRD + single broker

## Key Decisions & Tradeoffs
- Kafka local: Redpanda (simpler)
- Dapr install: dapr init -k
- Sidecar injection: Helm annotations
- Topic creation: Auto or init container
- State usage: Dapr state.postgresql (Neon)

## Implementation Sequence (12 Phases with Agent Assignment)
1. Minikube environment verification (BlueprintAgent)
2. Install Dapr on Minikube (K8sAgent)
3. Extend Helm chart for Dapr sidecars (HelmAgent)
...
12. Documentation & cleanup (OrchestratorAgent)
```

## Response snapshot

### Implementation Plan Created

Successfully created comprehensive implementation plan for Phase V Part B - Local Minikube + Dapr + Kafka Deployment.

**Plan File**: `specs/006-phase5-partb-local-deployment/plan.md`

### Implementation Phases (9 Phases, 45 Tasks)

| Phase | Focus | Tasks | Agent |
|-------|-------|-------|-------|
| 1 | Environment & Dapr | T601-T604 | K8sAgent |
| 2 | Kafka (Redpanda) | T605-T609 | HelmAgent, KafkaAgent |
| 3 | Helm Chart Extension | T610-T614 | HelmAgent |
| 4 | Dapr Components | T615-T619 | DaprAgent, HelmAgent |
| 5 | Application Deployment | T620-T624 | K8sAgent |
| 6 | Event Integration | T625-T629 | KafkaAgent, K8sAgent |
| 7 | Dapr Building Blocks | T630-T634 | DaprAgent |
| 8 | E2E Testing | T635-T639 | OrchestratorAgent |
| 9 | Documentation | T640-T645 | OrchestratorAgent |

### Key Decisions Documented

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Kafka Broker | Redpanda | Simpler, no Zookeeper |
| Dapr Install | `dapr init -k` | Official method |
| Sidecar Injection | Helm annotations | Helm-native |
| Topic Creation | Dapr auto-create | Less manual work |
| State Store | PostgreSQL (Neon) | Consistent with DB |

### Constitution Compliance

All 7 principles verified compliant:
- P1: Spec-Driven ✓
- P2: AI-Assisted Infrastructure ✓
- P3: Backward Compatibility ✓
- P4: Full Dapr Runtime ✓
- P5: Dapr-Exclusive ✓
- P6: Local Kafka ✓
- P7: Extend Phase IV Helm ✓

### Supporting Artifacts Created

| File | Purpose |
|------|---------|
| `research.md` | Technology decisions and rationale |
| `data-model.md` | Infrastructure entity documentation |
| `quickstart.md` | 10-command quick deploy guide |

### Helm Chart Structure Defined

```
helm/todo-chatbot/
├── values-dapr.yaml (NEW)
├── templates/
│   ├── backend-deployment.yaml (UPDATED: Dapr)
│   ├── frontend-deployment.yaml (UPDATED: Dapr)
│   ├── dapr/ (NEW)
│   │   ├── pubsub-kafka.yaml
│   │   ├── statestore.yaml
│   │   └── secretstore.yaml
│   └── kafka/ (NEW)
│       ├── redpanda-deployment.yaml
│       └── redpanda-service.yaml
```

## Outcome

- Impact: Complete implementation plan for Phase V Part B local deployment
- Tests: N/A - planning document
- Files: 4 files created (plan.md, research.md, data-model.md, quickstart.md)
- Next prompts: `/sp.tasks` for detailed task breakdown with test cases
- Reflection: User-provided architecture guided efficient plan creation; all constitution principles verified compliant

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
  - Architecture diagram included: ✓
  - Key decisions documented: ✓ (6 decisions with rationale)
  - Implementation phases defined: ✓ (9 phases, 45 tasks)
  - Agent assignments clear: ✓
  - Constitution compliance verified: ✓ (all 7 principles)
  - Success criteria mapped: ✓
  - Risks identified: ✓ (5 risks with mitigations)
  - Supporting artifacts created: ✓ (research.md, data-model.md, quickstart.md)
- Prompt variant (if applicable): User provided detailed architecture sketch
- Next experiment: Generate detailed tasks.md with AI-agent execution commands

📋 Architectural decision detected: Kafka broker selection (Redpanda vs Strimzi) and Dapr installation method. Document reasoning and tradeoffs? Run `/sp.adr phase5-partb-infrastructure-decisions`
