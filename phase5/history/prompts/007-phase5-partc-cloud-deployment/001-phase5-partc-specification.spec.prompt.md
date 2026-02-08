---
id: 001
title: Phase V Part C Cloud Deployment Specification
stage: spec
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 007-phase5-partc-cloud-deployment
branch: 007-phase5-partc-cloud-deployment
user: rvwaq
command: /sp.specify
labels: ["phase5", "partc", "cloud", "oke", "oracle", "dapr", "kafka", "cicd", "spec"]
links:
  spec: specs/007-phase5-partc-cloud-deployment/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/007-phase5-partc-cloud-deployment/spec.md
  - specs/007-phase5-partc-cloud-deployment/checklists/requirements.md
tests:
  - N/A (specification artifact - no code tests)
---

## Prompt

/sp.specify
# specs/specify.md - Hackathon II: Phase V - Part C: Cloud Deployment (Oracle OKE Focus)

## Project Overview
Deploy the complete AI-Powered Todo Chatbot application (with Phase III chatbot, Part A advanced features, Part B Dapr + Kafka logic) to a production-grade Kubernetes cluster on Oracle Cloud Always Free OKE (Oracle Kubernetes Engine).
Use full Dapr (Pub/Sub with Kafka, State, Jobs, Secrets, Service Invocation), connect to Redpanda Cloud (free serverless Kafka) or self-hosted Strimzi, set up basic CI/CD with GitHub Actions, and configure monitoring/logging — all with zero ongoing cost using Oracle Always Free tier.

## Current Phase
Phase V – Part C: Cloud Deployment on Oracle Cloud Always Free OKE (recommended for long-term free usage)

## Target Environment
- Oracle Cloud Infrastructure (OCI) Always Free Tier
- OKE Cluster: 4 OCPUs, 24GB RAM (Always Free – no credit card charge after signup)
- External Neon PostgreSQL (continued from previous phases)
- Kafka: Redpanda Cloud serverless (free tier) preferred, or Strimzi self-hosted on OKE

## Focus & Core Functionality
- Create OKE cluster using Oracle Cloud Console or OCI CLI
- Install Dapr on OKE cluster (full suite)
- Connect to Redpanda Cloud Kafka via Dapr pubsub component
- Deploy application using extended Helm chart from Phase IV/Part B
- Expose frontend publicly via LoadBalancer
- Set up GitHub Actions CI/CD pipeline for auto-deploy on push
- Add basic monitoring/logging (OCI Logging, kubectl logs, Dapr logs)

## Response snapshot

Created comprehensive specification for Phase V Part C: Cloud Deployment on Oracle OKE.

**Feature branch**: `007-phase5-partc-cloud-deployment`
**Spec file**: `specs/007-phase5-partc-cloud-deployment/spec.md`

Key specification contents:
1. **4 User Stories** (P1-P4):
   - US1: Cloud Cluster Setup & App Deployment (P1 MVP)
   - US2: Cloud Kafka Integration via Redpanda Cloud (P2)
   - US3: CI/CD Pipeline via GitHub Actions (P3)
   - US4: Monitoring, Logging & Documentation (P4)
2. **15 Functional Requirements** (FR-001 through FR-015)
3. **10 Measurable Success Criteria** (SC-001 through SC-010)
4. **5 Edge Cases** covering free tier limits, IP assignment, auth expiry
5. **Technical Architecture** with deployment diagram showing OKE + Redpanda Cloud + Neon + GitHub Actions
6. **Key Entities**: OKE Cluster, Dapr Components, Redpanda Cloud, CI/CD Pipeline, Cloud Values Override
7. **6 Risks & Mitigations** including ARM64 builds, resource limits, auth expiry
8. **8 Constraints** all tied to free tier and demo scope
9. **Quality Checklist**: All items pass, zero [NEEDS CLARIFICATION] markers

No clarification needed — user input was comprehensive for all decisions.

## Outcome

- Impact: Complete spec created for Phase V Part C cloud deployment on Oracle OKE
- Tests: N/A (specification artifact)
- Files: 2 files created (spec.md, checklists/requirements.md)
- Next prompts: /sp.plan for implementation planning, then /sp.tasks
- Reflection: User input was exceptionally detailed — covered provider choice (Oracle OKE), Kafka choice (Redpanda Cloud), CI/CD (GitHub Actions), and constraints (Always Free). No ambiguity needed resolution.

## Evaluation notes (flywheel)

- Failure modes observed: create-new-feature.ps1 ran from repo root instead of phase5; manual dir creation needed
- Graders run and results (PASS/FAIL): Quality checklist PASS (all items)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Run /sp.plan to generate implementation plan
