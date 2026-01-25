---
id: 002
title: Phase IV K8s Deployment Constitution
stage: constitution
date: 2026-01-22
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: waqas
command: /sp.constitution
labels: ["constitution", "phase4", "kubernetes", "aiops", "helm"]
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

/sp.constitution

# speckit.constitution - Hackathon II: Evolution of Todo (Phase IV - Local Kubernetes Deployment)

## Project
Phase IV: Local Kubernetes Deployment of the Complete AI-Powered Todo Chatbot (Phase III) on Minikube using Helm Charts and AIOps tools.

## Core Principles
- Strictly Spec-Driven Development: No infrastructure change without reference to a spec file or task
- No manual coding or manual kubectl/helm commands allowed outside AI-assisted flow
- All containerization, Helm chart generation, and Kubernetes operations must use AI agents (Gordon, kubectl-ai, kagent)
- Backward compatibility: The deployed application must retain all Phase III functionality (Cohere-powered chatbot, task management, user isolation, stateless chat endpoint)
- Reusability: Create blueprints and patterns that can be reused for future deployments
- Demonstrable AIOps: Heavy use of Gordon, kubectl-ai, and kagent must be visible in process and documentation

## Key Standards
- Tech Stack (strict for Phase IV):
  - Containerization: Docker Desktop with Gordon AI enabled
  - Orchestration: Minikube (local Kubernetes)
  - Packaging: Helm Charts
  - AIOps Tools: Gordon (Docker AI), kubectl-ai, kagent
- Docker Images:
  - Separate optimized images for frontend (Next.js standalone) and backend (FastAPI + Cohere agent)
  - Multi-stage builds mandatory
  - Images must run locally before Kubernetes deployment
- Helm Chart:
  - Single chart managing both frontend and backend deployments/services
  - ConfigMap for non-sensitive config
  - Secret for BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY
  - Templates generated primarily via kubectl-ai / kagent
- Kubernetes Resources:
  - 1 replica each by default (scalable via AI commands)
  - External Neon PostgreSQL (no local DB pod)
  - Local access via minikube service or port-forward
- AI-Assisted Operations:
  - Gordon must be used for Dockerfile generation/optimization
  - kubectl-ai and kagent must be used for Helm template generation and cluster operations

## Constraints
- Local deployment only (Minikube on Docker Desktop)
- External Neon DB connection via secret
- No Ingress controller required (use minikube service --url)
- No persistent volumes needed (stateless app + external DB)
- Resource limits suitable for laptop (no over-allocation)
- No cloud providers (DigitalOcean in Phase V only)
- If Gordon unavailable → fallback to standard Dockerfiles allowed but must be documented

## Success Criteria
- Both frontend and backend successfully containerized and run locally with docker run
- Docker images built and testable
- Complete Helm chart created and passes helm lint + dry-run
- Application successfully deployed to Minikube via helm install
- Both services running and accessible locally
- Full end-to-end functionality:
  - Login via Better Auth
  - Task CRUD via dashboard
  - Natural language task management via chatbot (Cohere agent working)
  - Conversation persistence after pod restart
- Demonstrated use of AIOps tools:
  - Gordon prompts in documentation/logs
  - kubectl-ai commands for deployment/scaling/debugging
  - kagent commands for health/analysis
- Clean documentation in README with exact deployment steps and AI commands used
- All agents (DockerAgent, HelmAgent, K8sAgent, BlueprintAgent) roles visible in process

## Non-Negotiables
- Never use manual docker build/kubectl/helm without AI assistance
- Never hardcode secrets — use Helm secrets or environment injection
- Never bypass spec-driven process — every action traceable to plan/tasks
- Never break Phase III functionality
- Gordon must be enabled and used (screenshot or log proof if needed)
- Final demo must show chatbot working inside Minikube-deployed app

## Bonus Alignment
- Clear demonstration of multi-agent orchestration (BlueprintAgent coordinating others)
- Extensive use of kubectl-ai and kagent commands
- Optimized resource usage and troubleshooting examples
- Reusable Helm blueprint for future phases

## Response snapshot

Updated constitution from v1.0.0 to v2.0.0 (MAJOR version bump due to phase transition).

Key changes:
- 6 Core Principles for Phase IV (Spec-Driven, AI-Assisted Only, Backward Compatibility, Reusable Blueprints, Demonstrable AIOps, Tech Stack)
- Docker Images standards (multi-stage, size targets <100MB frontend/<200MB backend)
- Helm Chart standards (single chart, ConfigMap, Secrets, kubectl-ai generation)
- Kubernetes Resources standards (1 replica, external Neon DB, minikube service access)
- AI-Assisted Operations table (Gordon, kubectl-ai, kagent)
- Non-Negotiables section (6 hard constraints)
- Bonus Alignment section (hackathon criteria)
- Success Criteria organized by phase (Docker, Helm, K8s, Functionality, Documentation)

Templates reviewed: plan-template.md, spec-template.md, tasks-template.md (no updates needed - generic structure)

## Outcome

- Impact: MAJOR constitution update for Phase IV Local Kubernetes Deployment
- Tests: null
- Files: 1 file updated (.specify/memory/constitution.md)
- Next prompts: /sp.specify for Phase IV feature specification
- Reflection: Constitution now fully aligned with Phase IV requirements and hackathon bonus criteria

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin spec creation using this constitution as foundation
