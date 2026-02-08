---
id: 005
title: Phase V Part C Cloud Deployment Constitution
stage: constitution
date: 2026-02-06
surface: agent
model: claude-opus-4-6
feature: 007-phase5-partc-cloud-deployment
branch: 1-phase5-parta-advanced-events
user: rvwaq
command: /sp.constitution
labels: ["phase5", "partc", "cloud", "deployment", "constitution", "aks", "gke", "doks", "oke", "cicd"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests:
  - N/A (constitution update - no code tests)
---

## Prompt

for phase5 part C
# speckit.constitution - Hackathon II: Evolution of Todo (Phase V - Part C: Cloud Deployment)

## Project
Phase V – Part C: Production-grade Cloud Deployment of the full AI-Powered Todo Chatbot with Dapr, Kafka, and CI/CD on Azure AKS, Google GKE, or DigitalOcean DOKS (Oracle OKE as free alternative).

## Core Principles
- Strictly Spec-Driven Development: No cloud resource, Helm change, Dapr component, or CI/CD step without spec/task reference
- No manual kubectl/helm/doctl/az/gcloud commands — use AI agents (kubectl-ai, kagent, HelmAgent, CloudDeployAgent) as much as possible
- Backward compatibility: Phase III chatbot, Phase IV local deploy, Part A features, Part B Dapr patterns must remain fully functional
- Production-ready mindset: High availability, external access, secrets security, monitoring/logging basics
- Cost control: Use free credits ($200 DigitalOcean, $300 Google, $200 Azure, Oracle Always Free OKE)
- Portability: Dapr abstraction so Kafka/DB can be swapped without code change

## Key Standards
- Cloud Provider Preference (choose one):
  - DigitalOcean Kubernetes (DOKS): $200 credit (60 days) or GitHub Student Pack (1 year)
  - Azure AKS: $200 credit (30 days) + free services
  - Google GKE: $300 credit (90 days)
  - Oracle OKE: Always Free (4 OCPUs, 24GB RAM) — recommended for long-term learning
- Dapr on Cloud:
  - Full Dapr: pubsub.kafka, state.postgresql, jobs (for reminders), secrets (kubernetes), service-invocation
  - Sidecar injection on all pods (frontend, backend, future consumers)
- Kafka:
  - Redpanda Cloud serverless (free tier) — recommended
  - Confluent Cloud ($400 credit)
  - Self-hosted Strimzi on cluster (free but compute cost)
  - Topics: task-events, reminders, task-updates
- CI/CD:
  - GitHub Actions workflow: build Docker images → push to registry → helm upgrade on cluster
- Monitoring & Logging Basics:
  - kubectl logs + Dapr logs
  - Optional: DigitalOcean monitoring, Azure Monitor, or Google Cloud Logging

## Constraints
- Use free credits / always free tiers only (no paid overage in demo)
- External Neon PostgreSQL continue (Dapr state for cache only)
- Public access: LoadBalancer service or Ingress for frontend
- Secrets: Use Dapr kubernetes-secrets or cloud secret manager
- No vendor lock-in: Dapr makes Kafka/DB swap possible
- Demo video: Show cloud URL, advanced features, event flow, CI/CD run

## Success Criteria (Part C only)
- Cloud cluster created (DOKS/AKS/GKE/OKE)
- kubectl configured to connect to cloud cluster
- Dapr installed on cloud cluster (dapr init -k)
- Kafka connected (Redpanda Cloud or Strimzi)
- Helm chart deployed with Dapr sidecars and components
- App publicly accessible
- Full flow works: login → dashboard → chatbot → advanced features → events published to cloud Kafka
- CI/CD pipeline: GitHub Actions builds & deploys on push (show in video)
- Monitoring/logging: Basic logs accessible (kubectl logs, Dapr logs)
- Documentation: Cloud signup steps, cluster creation, Helm values, CI/CD YAML, demo URL

## Non-Negotiables
- Never hardcode secrets — use Dapr secrets or cloud secret store
- Never expose sensitive env vars in Helm values
- Never break Phase III/IV/Part A/Part B functionality
- Use free tier/credit only — document cost (should be $0 for demo)

## Response snapshot

Updated constitution from v4.0.0 to v5.0.0 (MAJOR version bump) for Phase V Part C: Cloud Deployment.

Key changes:
1. **Mission Statement**: Updated from local Minikube to production-grade cloud K8s deployment
2. **9 Core Principles**: Added Principle 8 (Cost Control) and Principle 9 (CI/CD Pipeline Required); expanded existing principles for cloud context
3. **Cloud Provider Selection** (Section 3): New section with 4 provider options, cluster requirements, container registry options
4. **Dapr on Cloud** (Section 4): Updated components for cloud Kafka with SASL authentication
5. **Cloud Kafka Options** (Section 5): Redpanda Cloud, Confluent Cloud, self-hosted Strimzi
6. **Helm Cloud Extensions** (Section 6): values-cloud.yaml override strategy
7. **CI/CD Pipeline** (Section 7): GitHub Actions workflow structure and required secrets
8. **Public Access & Ingress** (Section 8): LoadBalancer, Ingress, SSL/TLS options
9. **Monitoring & Logging** (Section 9): Required and optional monitoring tools
10. **8 Non-Negotiables**: Expanded from 6 to 8, adding CI/CD and credential security rules
11. **Success Criteria**: 8 categories covering cluster, Dapr, Kafka, Helm, public access, CI/CD, monitoring, documentation

Template consistency propagation verified: plan-template.md, spec-template.md, tasks-template.md all compatible.

## Outcome

- Impact: Constitution updated to v5.0.0 covering full cloud deployment governance for Phase V Part C
- Tests: N/A (constitution update)
- Files: 1 file modified (.specify/memory/constitution.md)
- Next prompts: /sp.specify for Phase V Part C spec, then /sp.plan, /sp.tasks
- Reflection: Clean phase transition from local to cloud. The 2 new principles (Cost Control, CI/CD) are critical for cloud governance that didn't apply locally.

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (governance artifact)
- Prompt variant (if applicable): null
- Next experiment (smallest change to try): Create Part C spec using this constitution as governance baseline
