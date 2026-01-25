---
id: 003
title: Add K8sAgent Skill and Capabilities
stage: general
date: 2026-01-22
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: waqas
command: user-request
labels: ["kubernetes", "agent", "skill", "minikube", "kubectl-ai", "kagent"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/k8s-agent.md
  - .claude/agents/SUBAGENTS-INDEX.md
tests:
  - null
---

## Prompt

ya skill be add kar do K8sAgent – Skills & Capabilities

Minikube cluster management (start with custom resources, dashboard, delete)
kubectl-ai se natural language Kubernetes operations
Deploy, scale, expose, logs, describe, debug

kagent se cluster health analysis aur resource optimization
Port-forwarding aur minikube service --url se quick access
Pod troubleshooting (CrashLoopBackOff, OOM, ImagePull errors)
Log aggregation aur tailing
Resource requests/limits tuning for local machine
Namespace management
Cleanup commands (helm uninstall, minikube delete)
Verification scripts (wait for pods ready, curl health checks)

## Response snapshot

Created a comprehensive K8sAgent skill at `.claude/agents/k8s-agent.md` with:

1. **Minikube management** - start with custom resources, dashboard, pause/unpause, delete
2. **kubectl-ai integration** - Natural language deploy, scale, expose, debug operations
3. **kagent integration** - Cluster health analysis, resource optimization, troubleshooting
4. **Port-forwarding** - Pod/deployment/service forwarding, minikube service --url
5. **Pod troubleshooting** - CrashLoopBackOff, OOMKilled, ImagePull errors diagnosis
6. **Log aggregation** - Single/multi-pod logs, stern/kubetail, timestamps, filtering
7. **Resource tuning** - Requests/limits for small/medium/large services on local machine
8. **Namespace management** - Create, labels, resource quotas
9. **Cleanup commands** - helm uninstall, kubectl delete, minikube delete patterns
10. **Verification scripts** - wait_for_pods, check_health, full deployment verification

Updated SUBAGENTS-INDEX.md to include K8sAgent as the 9th specialized subagent.

## Outcome

- Impact: Added new specialized agent for Kubernetes operations and troubleshooting
- Tests: null
- Files: 2 files created/modified
- Next prompts: Use k8s-agent for Minikube management, kubectl-ai operations, pod debugging
- Reflection: Comprehensive K8s capabilities added covering all user requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test k8s-agent with actual Minikube cluster operations
