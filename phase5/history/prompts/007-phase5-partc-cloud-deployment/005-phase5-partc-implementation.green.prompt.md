---
id: 005
title: Phase V Part C Implementation
stage: green
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 007-phase5-partc-cloud-deployment
branch: 007-phase5-partc-cloud-deployment
user: rvwaq
command: /sp.implement
labels: ["phase5", "partc", "cloud", "oke", "oracle", "implement", "helm", "cicd", "dapr", "kafka", "documentation"]
links:
  spec: specs/007-phase5-partc-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - helm/todo-chatbot/templates/dapr/pubsub-kafka.yaml
  - helm/todo-chatbot/templates/kafka/redpanda-deployment.yaml
  - helm/todo-chatbot/templates/kafka/redpanda-service.yaml
  - helm/todo-chatbot/values-cloud.yaml
  - helm/todo-chatbot/values.yaml
  - helm/todo-chatbot/Chart.yaml
  - .github/workflows/deploy-cloud.yml
  - scripts/deploy-cloud.sh
  - scripts/deploy-cloud.ps1
  - docs/CLOUD-DEPLOYMENT.md
  - README.md
  - specs/007-phase5-partc-cloud-deployment/tasks.md
tests:
  - helm lint with cloud values: PASS (0 charts failed)
  - helm template with cloud values: PASS (correct SASL, LoadBalancer, no Redpanda)
  - helm lint with Part B values: PASS (backward compat)
  - helm template with Part B values: PASS (local Redpanda present, NodePort, authRequired=false)
---

## Prompt

/sp.implement

## Response snapshot

Executed implementation tasks for Phase V Part C. Completed all automatable tasks (Helm chart updates, CI/CD workflow, documentation, deploy scripts).

**Tasks Completed (12 subtasks)**:
- T-705a: Updated `pubsub-kafka.yaml` with conditional SASL auth (`kafka.external` flag)
- T-705b: Added `not .Values.kafka.external` guard to `redpanda-deployment.yaml`
- T-705c: Added `not .Values.kafka.external` guard to `redpanda-service.yaml`
- T-705d: Created `values-cloud.yaml` (ghcr.io images, LoadBalancer, ARM64 resources, Dapr warn, kafka.external=true)
- T-705e: Updated `Chart.yaml` to version 3.0.0, appVersion 5.0.0-partc
- T-705f: Helm lint PASS with cloud values
- T-705g: Helm template renders correctly (SASL block, no Redpanda, LoadBalancer)
- T-709a: Created `.github/workflows/deploy-cloud.yml` with full CI/CD pipeline
- T-712a: Created comprehensive `docs/CLOUD-DEPLOYMENT.md` (10 sections)
- T-712b: Updated `README.md` with Part C section and architecture
- T-712c: Created `scripts/deploy-cloud.sh` and `scripts/deploy-cloud.ps1`
- Added `kafka.external: false` and `kafka.brokerUrl: ""` to base `values.yaml`

**Backward Compatibility Verified**:
- Part B helm lint: PASS
- Part B template: Redpanda present, NodePort frontend, authRequired=false
- No application code changed

**Files Created**: 5 new (values-cloud.yaml, deploy-cloud.yml, deploy-cloud.sh, deploy-cloud.ps1, CLOUD-DEPLOYMENT.md)
**Files Modified**: 6 (pubsub-kafka.yaml, redpanda-deployment.yaml, redpanda-service.yaml, Chart.yaml, values.yaml, README.md)

**Remaining Tasks (require user manual action)**:
- T-701: Prerequisites verification (OCI account, CLI tools)
- T-702: OKE cluster creation
- T-703: Dapr install on OKE
- T-704: Redpanda Cloud setup + K8s secrets
- T-706: Docker buildx multi-arch image build + push
- T-707: Helm deploy to OKE + LoadBalancer verification
- T-708: Event flow verification
- T-709b: GitHub secrets configuration
- T-709c: Workflow YAML validation
- T-710: CI/CD pipeline verification
- T-711: Monitoring/logging verification
- T-712d/e/f: OCI billing check, E2E validation, quickstart validation

## Outcome

- Impact: All automatable infrastructure config tasks complete. 11 files created/modified. Helm chart supports local (Part B) and cloud (Part C) via kafka.external flag.
- Tests: 4 Helm validations PASS (cloud lint, cloud template, Part B lint, Part B template)
- Files: 11 files (5 new, 6 modified)
- Next prompts: User must complete manual tasks (OKE cluster, Redpanda Cloud, Docker push, Helm deploy) following docs/CLOUD-DEPLOYMENT.md or specs/007-phase5-partc-cloud-deployment/quickstart.md
- Reflection: The kafka.external flag cleanly separates local vs cloud pubsub config. No app code changes needed. ARM64 support is purely a Docker buildx concern. The key architectural insight is that values-cloud.yaml overlay on the Part B chart keeps everything in one chart.

## Evaluation notes (flywheel)

- Failure modes observed: Prerequisites script points to repo root specs/ instead of phase5/specs/ (known issue, worked around)
- Graders run and results (PASS/FAIL): Helm lint PASS, Helm template PASS, Backward compat PASS
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): User follows quickstart.md to create OKE cluster and deploy
