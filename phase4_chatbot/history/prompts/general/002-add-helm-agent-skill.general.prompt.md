---
id: 002
title: Add HelmAgent Skill and Capabilities
stage: general
date: 2026-01-22
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: waqas
command: user-request
labels: ["helm", "agent", "skill", "kubernetes", "charts"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/helm-agent.md
  - .claude/agents/SUBAGENTS-INDEX.md
tests:
  - null
---

## Prompt

aik skill or add kar do HelmAgent – Skills & Capabilities

Complete Helm chart scaffolding (Chart.yaml, values.yaml, templates/)
AI-assisted template generation via kubectl-ai prompts
kagent se values.yaml aur resource optimization
Deployment, Service, ConfigMap, Secret templates banana
Environment-specific values files (values-local.yaml, values-prod.yaml)
Secret management (sealed secrets ya external secrets suggestion)
Helm hooks for migrations aur init containers
Dependency management (subcharts if needed)
helm lint, helm template, helm install --dry-run validation
Upgrade strategies aur rollback plans

## Response snapshot

Created a comprehensive HelmAgent skill at `.claude/agents/helm-agent.md` with:

1. **Complete chart scaffolding** - Standard Helm chart structure with all files
2. **Chart.yaml template** - Full metadata, maintainers, dependencies
3. **kubectl-ai prompts** - AI-assisted generation for Deployment, Service, Ingress, HPA
4. **kagent integration** - Values optimization and resource tuning commands
5. **Template examples** - Deployment, Service, ConfigMap with best practices
6. **Environment-specific values** - values.yaml, values-local.yaml, values-prod.yaml
7. **Secret management** - Sealed Secrets and External Secrets Operator patterns
8. **Helm hooks** - Pre-install/upgrade migration jobs, init containers
9. **Dependency management** - Subchart configuration (PostgreSQL, Redis)
10. **Validation commands** - lint, template, dry-run, API deprecation checks
11. **Upgrade/Rollback strategies** - Safe upgrade with atomic, rollback commands

Updated SUBAGENTS-INDEX.md to include HelmAgent as the 8th specialized subagent.

## Outcome

- Impact: Added new specialized agent for Kubernetes Helm chart development
- Tests: null
- Files: 2 files created/modified
- Next prompts: Use helm-agent for Helm chart creation, kubectl-ai integration, secret management
- Reflection: Comprehensive Helm capabilities added covering all user requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test helm-agent with actual chart scaffolding
