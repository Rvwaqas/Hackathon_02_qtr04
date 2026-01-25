---
id: 001
title: Add DockerAgent Skill and Capabilities
stage: general
date: 2026-01-22
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: main
user: waqas
command: user-request
labels: ["docker", "agent", "skill", "containerization"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/agents/docker-agent.md
  - .claude/agents/SUBAGENTS-INDEX.md
tests:
  - null
---

## Prompt

skill add kar do DockerAgent – Skills & Capabilities

Multi-stage Dockerfile generation for Next.js (standalone output, minimal node image)
Multi-stage Dockerfile for FastAPI (uv for dependency management, slim python base)
Gordon AI prompts craft karna (e.g., "docker ai create optimized Dockerfile for Next.js standalone")
Image size optimization (under 100MB frontend, under 200MB backend)
.dockerignore files banana for faster builds
Local testing: docker run with environment variables aur port mapping
Multi-platform build support (amd64/arm64)
Security scanning suggestions (trivy integration)
Dockerfile linting aur best practices enforcement
Debug common build errors (layer caching, permission issues)

## Response snapshot

Created a comprehensive DockerAgent skill at `.claude/agents/docker-agent.md` with:

1. **Multi-stage Dockerfile templates** for Next.js (standalone mode, <100MB) and FastAPI (uv, <200MB)
2. **Gordon AI integration** with optimized prompts for Dockerfile generation
3. **Image optimization rules** including layer ordering, explicit COPY, Alpine/Slim bases
4. **.dockerignore best practices** template for Node.js and Python projects
5. **Multi-platform build support** using docker buildx for amd64/arm64
6. **Security scanning** with Trivy commands and CI integration
7. **Dockerfile linting** with Hadolint rules and fixes
8. **Local testing protocol** with docker run examples and health check verification
9. **Debug guides** for common issues: layer caching, permissions, context size, multi-stage COPY

Updated SUBAGENTS-INDEX.md to include DockerAgent as the 7th specialized subagent.

## Outcome

- Impact: Added new specialized agent for Docker containerization tasks
- Tests: null
- Files: 2 files created/modified
- Next prompts: Use docker-agent for Next.js/FastAPI containerization, Gordon AI integration
- Reflection: Comprehensive Docker capabilities added covering all user requirements

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Test docker-agent with actual Dockerfile generation
