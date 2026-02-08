---
id: 003
title: Phase V Part C Task Breakdown
stage: tasks
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 007-phase5-partc-cloud-deployment
branch: 007-phase5-partc-cloud-deployment
user: rvwaq
command: /sp.tasks
labels: ["phase5", "partc", "cloud", "oke", "oracle", "tasks", "breakdown", "dapr", "kafka", "cicd"]
links:
  spec: specs/007-phase5-partc-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-phase5-partc-cloud-deployment/tasks.md
tests:
  - N/A (task breakdown artifact - no code tests)
---

## Prompt

/sp.tasks
You are an expert spec-driven developer working on Hackathon II: Phase V - Part C (Cloud Deployment on Oracle Always Free OKE). Follow this exact task list in strict order. Task numbering T-701 through T-712 covering Oracle account verification, kubectl config, Dapr install, Redpanda Cloud, Helm chart updates, deployment, CI/CD, monitoring, E2E validation, and documentation.

## Response snapshot

Generated comprehensive tasks.md with 12 major task groups (T-701 through T-712) expanded into 50+ subtasks organized by 4 user stories.

**Task Structure**:
- **Phase 1**: Research & Prerequisites (T-701, 6 subtasks)
- **Phase 2 (US1)**: Cluster Setup & App Deployment (T-702 through T-707, 25 subtasks)
  - T-702: OKE Cluster creation (3 subtasks)
  - T-703: Dapr installation (3 subtasks)
  - T-705: Helm chart cloud extensions (7 subtasks)
  - T-706: Multi-arch Docker images (5 subtasks)
  - T-707: Application deployment (6 subtasks)
- **Phase 3 (US2)**: Kafka Integration (T-704, T-708, 11 subtasks)
- **Phase 4 (US3)**: CI/CD Pipeline (T-709, T-710, 9 subtasks)
- **Phase 5 (US4)**: Monitoring & Documentation (T-711, T-712, 10 subtasks)

**Traceability**:
- All 15 FRs mapped to specific tasks
- All 10 SCs mapped to specific tasks
- All 4 User Stories have dedicated phases with checkpoints
- Critical path and parallel opportunities documented
- Dependencies and execution order defined

**Key Design Decisions**:
- T-704 (Redpanda) can run in parallel with T-702/T-703 to save time
- Helm chart changes (T-705) include conditional SASL via `kafka.external` flag
- Redpanda local deployment wrapped with `not .Values.kafka.external` guard
- CI/CD workflow follows contract in `contracts/github-actions-schema.yml`
- No application code changes — infrastructure/config only

## Outcome

- Impact: Complete task breakdown with 50+ subtasks, full FR/SC traceability, dependency graph, and parallel opportunities
- Tests: N/A (task breakdown artifact)
- Files: 1 file created (tasks.md)
- Next prompts: /sp.implement to execute tasks T-701 through T-712 in order
- Reflection: Tasks are purely infrastructure — no app code changes needed. The critical insight is that `kafka.external` flag in Helm values controls the local-vs-cloud pubsub configuration switch. ARM64 is handled entirely by Docker buildx, not Dockerfile changes.

## Evaluation notes (flywheel)

- Failure modes observed: Context session ran out during initial task generation; completed in continuation
- Graders run and results (PASS/FAIL): FR traceability PASS (15/15), SC traceability PASS (10/10), US coverage PASS (4/4)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run /sp.implement to begin executing tasks starting with T-701
