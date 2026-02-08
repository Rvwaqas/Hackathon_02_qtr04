---
id: 004
title: Phase V Part B Minikube Dapr Kafka Constitution
stage: constitution
date: 2026-02-03
surface: agent
model: claude-opus-4-5-20251101
feature: 006-phase5-partb-local-deployment
branch: 1-phase5-parta-advanced-events
user: waqas
command: /sp.constitution
labels: ["constitution", "phase5", "partb", "minikube", "dapr", "kafka", "redpanda", "deployment"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - null
---

## Prompt

```text
/sp.constitution
# speckit.constitution - Hackathon II: Evolution of Todo (Phase V - Part B: Local Minikube + Dapr + Kafka)

## Project
Phase V – Part B: Deploy the extended Phase V application (with advanced features and Dapr event publishing code) on local Minikube with full Dapr and local Kafka (Redpanda/Strimzi)

## Core Principles
- Strictly Spec-Driven: No deployment, component, or infra change without spec/task
- No manual kubectl/helm/dapr commands — use AI agents (kubectl-ai, kagent, HelmAgent, etc.)
- Backward compatibility: Phase III/IV functionality + Part A features intact
- Full Dapr usage: sidecars on every pod, all 5 building blocks (Pub/Sub, State, Jobs, Secrets, Service Invocation)
- Local Kafka: Redpanda Docker container (easy) or Strimzi operator (learning)
- Stateless & observable: Use Dapr for abstraction, logs for event verification
- Reusability: Extend Phase IV Helm chart + add Dapr/Kafka components

## Key Standards
[... Minikube, Dapr, Kafka, Helm standards ...]

## Constraints
- Local Minikube only (no cloud in Part B)
- External Neon DB continue (Dapr state.postgresql for cache only)
- Kafka local (no Redpanda Cloud yet — Part C)
- Dapr Jobs API for reminder scheduling (not cron bindings)
- No new pods for consumers yet (just publish + log verification)

## Success Criteria
[... Minikube, Dapr, Kafka, Application criteria ...]

## Non-Negotiables
- Never bypass Dapr for Pub/Sub or Jobs
- Never use direct Kafka client in code
- Never break Part A features or Phase III/IV functionality
- All infra traceable to AI-assisted commands (kubectl-ai/kagent)
- Local only — no cloud credentials in Part B
```

## Response snapshot

### Constitution Updated to v4.0.0

Updated the project constitution from v3.0.0 (Part A code-only) to v4.0.0 (Part B infrastructure deployment).

**Version Change**: v3.0.0 → v4.0.0 (MAJOR)

**Rationale**: Phase transition from code-only implementation to full Minikube + Dapr + Kafka infrastructure deployment.

### Modified Principles

| Old Principle | New Principle |
|---------------|---------------|
| No Manual Coding Allowed | AI-Assisted Infrastructure Only |
| Event-Driven Priority | Full Dapr Runtime (5 building blocks) |
| Dapr-Exclusive | Expanded with specific components |
| Reusability First | Extend Phase IV Helm Charts |

### Added Sections

1. **Deployment Target** - Minikube cluster standards (4GB RAM, 2 CPUs, Docker driver)
2. **Dapr Installation & Components** - `dapr init -k`, pubsub.kafka, state.postgresql, jobs, secrets
3. **Kafka/Redpanda Deployment** - Option 1: Redpanda (simple), Option 2: Strimzi (learning)
4. **Helm Chart Extensions** - Dapr sidecar annotations, new templates required
5. **Infrastructure Testing** - Sidecar verification, Pub/Sub test, Jobs API test, E2E test

### Removed Sections

- Database Extensions (Part A - complete)
- API Extensions (Part A - complete)
- Cohere Agent Updates (Part A - complete)

### Key Standards Defined

- **Minikube**: `minikube start --memory=4096 --cpus=2 --driver=docker`
- **Dapr**: `dapr init -k --wait` with 4 components configured
- **Kafka**: Redpanda single-container or Strimzi operator + single-broker
- **Helm**: Extend Phase IV charts with Dapr annotations
- **Testing**: Sidecar logs, rpk topic consume, Jobs API callbacks

### Success Criteria (Part B)

1. Minikube cluster + Dapr initialized
2. Kafka/Redpanda pods healthy
3. Helm deploy with Dapr sidecars
4. Task events visible in Kafka topics
5. Jobs API working (schedule/callback)
6. Application fully functional in Minikube
7. Full documentation provided

## Outcome

- Impact: Constitution v4.0.0 established for Part B infrastructure deployment
- Tests: N/A - governance document
- Files: 1 file updated (.specify/memory/constitution.md)
- Next prompts: `/sp.specify` for Phase V Part B feature specification
- Reflection: Clear separation between Part A (code) and Part B (infrastructure) established

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS
  - All 7 principles defined with rationale: ✓
  - Deployment target specified: ✓
  - Dapr components detailed: ✓
  - Kafka options documented: ✓
  - Helm extensions outlined: ✓
  - Testing procedures defined: ✓
  - Success criteria checklist: ✓
  - Non-negotiables clear: ✓
  - Version history updated: ✓
- Prompt variant (if applicable): N/A
- Next experiment: Proceed to specification for Part B deployment tasks
