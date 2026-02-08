---
id: 002
title: Phase V Part C Implementation Plan
stage: plan
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 007-phase5-partc-cloud-deployment
branch: 007-phase5-partc-cloud-deployment
user: rvwaq
command: /sp.plan
labels: ["phase5", "partc", "cloud", "oke", "oracle", "plan", "architecture", "cicd", "dapr", "kafka"]
links:
  spec: specs/007-phase5-partc-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-phase5-partc-cloud-deployment/plan.md
  - specs/007-phase5-partc-cloud-deployment/quickstart.md
  - specs/007-phase5-partc-cloud-deployment/contracts/dapr-cloud-pubsub.yaml
  - specs/007-phase5-partc-cloud-deployment/contracts/helm-cloud-values.yaml
  - specs/007-phase5-partc-cloud-deployment/contracts/github-actions-schema.yml
tests:
  - N/A (plan artifact - no code tests)
---

## Prompt

/sp.plan
# specs/plan.md - Hackathon II: Phase V - Part C: Cloud Deployment (Oracle OKE Focus)

## Architecture Sketch (Part C – Cloud Production Level)
Full application deployed on Oracle Cloud Always Free OKE cluster with Dapr sidecars, Redpanda Cloud Kafka, public LoadBalancer, CI/CD, and basic logging.
Oracle Cloud (OKE Cluster - Always Free)
├── Node Pool (4 OCPUs, 24GB RAM)
│   ├── Pod: todo-frontend (Next.js + ChatKit)
│   │   └── Dapr Sidecar
│   ├── Pod: todo-backend (FastAPI + Cohere Agent + MCP)
│   │   └── Dapr Sidecar
│   └── LoadBalancer Service → Public IP/URL (frontend access)
├── Dapr Components (deployed as ConfigMaps)
│   ├── pubsub.kafka → Redpanda Cloud (free serverless)
│   ├── state.postgresql → Neon DB (cache)
│   ├── jobs → scheduled reminders
│   ├── secrets.kubernetes → API keys
│   └── service-invocation → internal calls
[...]

## Response snapshot

Created comprehensive implementation plan for Phase V Part C: Cloud Deployment on Oracle OKE.

**8 Phases** covering the full deployment lifecycle:
1. **Phase 0: Research** — OKE Always Free shapes, Redpanda Cloud, ARM64 Docker images
2. **Phase 1: Cloud Account & Cluster** — Oracle signup, OKE creation, Dapr install
3. **Phase 2: Redpanda Cloud Kafka** — Account setup, topics, K8s secrets
4. **Phase 3: Helm Chart Cloud Extensions** — values-cloud.yaml, conditional SASL pubsub, Chart update
5. **Phase 4: Multi-Arch Docker Images** — ARM64+AMD64 buildx, ghcr.io push
6. **Phase 5: Application Deployment** — Helm deploy, LoadBalancer, E2E test
7. **Phase 6: Event Flow Verification** — Pub/Sub test, all 5 Dapr blocks
8. **Phase 7: CI/CD Pipeline** — GitHub Actions workflow, 12 secrets
9. **Phase 8: Monitoring & Documentation** — kubectl logs, CLOUD-DEPLOYMENT.md

**Key Architecture Decisions**:
- Oracle OKE Always Free (ARM64 Ampere A1, 4 OCPU/24GB) — permanent free tier
- Redpanda Cloud serverless — zero ops, free tier
- ghcr.io — free container registry, native GitHub Actions integration
- values-cloud.yaml overlay — reuse Part B chart, no new charts
- Multi-arch Docker buildx — ARM64 for OKE, AMD64 for local dev
- LoadBalancer (not Ingress) — simplest public access, free on OCI

**Contracts Created**:
- `dapr-cloud-pubsub.yaml`: Redpanda Cloud SASL/SCRAM Dapr component
- `helm-cloud-values.yaml`: Full cloud values override
- `github-actions-schema.yml`: Complete CI/CD workflow contract
- `quickstart.md`: 10-step deployment guide

All 9 constitution principles verified COMPLIANT. All 7 non-negotiable gates PASS.

## Outcome

- Impact: Complete implementation plan covering Oracle OKE + Redpanda Cloud + GitHub Actions CI/CD
- Tests: N/A (plan artifact)
- Files: 5 files created (plan.md, quickstart.md, 3 contracts)
- Next prompts: /sp.tasks for task breakdown, then /sp.implement
- Reflection: ARM64 requirement is the key technical challenge — OKE Always Free uses Ampere A1 processors. Docker buildx multi-platform builds handle this cleanly. No app code changes needed.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): Constitution check PASS (9/9 principles)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run /sp.tasks to generate task breakdown
