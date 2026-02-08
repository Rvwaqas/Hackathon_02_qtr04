# Skills Index - Hackathon II

## Overview
This document lists all the skills you need for the entire hackathon project. Each skill is a reusable capability that Claude Code can use when building different phases.

---

## Core Development Skills

### 1. **spec-driven-implementation.md**
- **Purpose**: Follow Spec-Driven Development workflow strictly
- **Used in**: ALL Phases (1-5)
- **Key Features**:
  - Read constitution, specify, plan, tasks before coding
  - Add task references in code comments
  - Never freestyle or add unspecified features
  - Stop and ask when specs are unclear

### 2. **python-fastapi-dev.md**
- **Purpose**: Build FastAPI backends with SQLModel ORM
- **Used in**: Phases 2, 3, 4, 5
- **Key Features**:
  - Async/await patterns
  - REST API endpoints
  - JWT authentication middleware
  - Database integration (Neon)
  - Pydantic validation

### 3. **nextjs-app-router-dev.md**
- **Purpose**: Build Next.js 16 frontends with App Router
- **Used in**: Phases 2, 3, 4, 5
- **Key Features**:
  - Server Components (default)
  - Client Components (interactive)
  - Better Auth integration
  - Type-safe API client
  - Tailwind CSS styling

---

## AI/Agent Skills

### 4. **mcp-server-builder.md**
- **Purpose**: Build MCP servers with AI-callable tools
- **Used in**: Phase 3, 4, 5
- **Key Features**:
  - Define tool schemas with Pydantic
  - Implement MCP tools (add_task, list_tasks, etc.)
  - JSON response format
  - Error handling
  - OpenAI Agents SDK integration

### 5. **openai-agents-sdk-dev.md** *(You need to create this)*
- **Purpose**: Build stateless AI agents using OpenAI SDK
- **Used in**: Phase 3, 4, 5
- **Key Features**:
  - Stateless chat endpoint
  - Conversation history from database
  - Tool calling with MCP
  - Message persistence

### 6. **chatkit-integration.md** *(You need to create this)*
- **Purpose**: Implement OpenAI ChatKit UI
- **Used in**: Phase 3, 4, 5
- **Key Features**:
  - ChatKit component setup
  - Domain allowlist configuration
  - Connect to backend chat API
  - Message rendering

---

## Database & Auth Skills

### 7. **neon-postgres-setup.md** *(You need to create this)*
- **Purpose**: Configure Neon serverless database
- **Used in**: Phases 2, 3, 4, 5
- **Key Features**:
  - Connection string setup
  - SQLModel migrations
  - Async session management
  - Environment variables

### 8. **better-auth-jwt.md** *(You need to create this)*
- **Purpose**: Implement Better Auth with JWT
- **Used in**: Phases 2, 3, 4, 5
- **Key Features**:
  - Better Auth configuration
  - JWT token issuance
  - FastAPI JWT verification
  - User authentication endpoints

---

## Cloud Native Skills

### 9. **docker-kubernetes-deployment.md**
- **Purpose**: Containerize and deploy to Kubernetes
- **Used in**: Phases 4, 5
- **Key Features**:
  - Multi-stage Dockerfiles
  - Docker Compose for local dev
  - Helm chart creation
  - Kubernetes deployments/services
  - Secrets management
  - kubectl-ai / kagent usage
  - Minikube and cloud deployment

### 10. **kafka-dapr-integration.md**
- **Purpose**: Event-driven architecture with Kafka + Dapr
- **Used in**: Phase 5
- **Key Features**:
  - Kafka setup (Strimzi or Redpanda)
  - Dapr installation
  - Pub/Sub components
  - Event publishing/consuming
  - State management
  - Jobs API for scheduling
  - Microservices architecture

### 11. **dapr-sidecar-integration.md** (NEW)
- **Purpose**: Complete Dapr sidecar integration for distributed apps
- **Used in**: Phase 5
- **Key Features**:
  - Dapr component YAML generation (pubsub.kafka, state.postgresql, jobs, secrets)
  - Event publishing via Dapr Pub/Sub HTTP API
  - State management for conversation history
  - Scheduled reminders using Dapr Jobs API
  - Service invocation with automatic retries
  - Helm annotations for sidecar injection
  - Troubleshooting guide (logs, health checks)
  - **Rule**: All infrastructure access via Dapr sidecar only (localhost:3500)

### 12. **kafka-event-architecture.md** (NEW)
- **Purpose**: Design event-driven systems with Kafka via Dapr Pub/Sub
- **Used in**: Phase 5
- **Key Features**:
  - Topic definitions (task-events, reminders, task-updates)
  - CloudEvents JSON schemas for all event types
  - Publishing via Dapr (`localhost:3500/v1.0/publish`)
  - Consumer patterns (Recurring Service, Notification Service)
  - Partitioning strategy (user_id as key for ordering)
  - Redpanda Cloud setup (serverless, free tier)
  - Strimzi operator installation + Kafka cluster YAML
  - Idempotency patterns and Dead Letter Queues
  - **Rule**: NO direct kafka-python, all via Dapr Pub/Sub

### 13. **cloud-kubernetes-deployment.md** (NEW)
- **Purpose**: Deploy to production cloud Kubernetes (DOKS, AKS, GKE)
- **Used in**: Phase 5
- **Key Features**:
  - DigitalOcean DOKS cluster creation via `doctl`
  - kubectl context switching and config management
  - Helm value overrides for cloud (replicas=2+, HPA, resources)
  - LoadBalancer service for public access
  - NGINX Ingress controller setup
  - Dapr installation on cloud (`dapr init -k`)
  - Strimzi/Redpanda deployment on cloud K8s
  - Secrets management (Kubernetes secrets)
  - GitHub Actions CI/CD workflow
  - Cost estimation & free tier tips ($200 DO credit)
  - **Recommendation**: DOKS for simplicity and cost-effectiveness

### 14. **phase5-orchestration.md** (NEW)
- **Purpose**: Central coordination for entire Phase V workflow
- **Used in**: Phase 5
- **Key Features**:
  - Full workflow orchestration (FeatureAgent → DaprAgent → KafkaAgent → CloudDeployAgent)
  - Cross-agent coordination and data handoffs
  - Validation checkpoints after each agent
  - Regression testing checklist (Phase III/IV compatibility)
  - Agent delegation protocol with success criteria
  - Final README Phase V section generation
  - Demo video script (90 seconds)
  - Bonus points alignment check (event-driven, Dapr, CI/CD)
  - Risk assessment (credit expiry, rate limits, costs)
  - Progress tracking templates
  - **Rule**: NEVER skip steps or change execution order

---

## Additional Skills You Should Create

### 11. **openai-agents-sdk-dev.md**
Build this skill for:
- OpenAI Agents SDK setup
- Stateless agent architecture
- Tool calling patterns
- Conversation state management
- Message persistence

### 12. **chatkit-integration.md**
Build this skill for:
- ChatKit UI component
- Domain allowlist setup
- API connection
- Message rendering
- Streaming support

### 13. **neon-postgres-setup.md**
Build this skill for:
- Neon account setup
- Connection string format
- Database creation
- SQLModel migrations
- Connection pooling

### 14. **better-auth-jwt.md**
Build this skill for:
- Better Auth configuration
- JWT plugin setup
- FastAPI integration
- Token verification
- User session management

---

## Skills Usage by Phase

| Skill | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Phase 5 |
|-------|---------|---------|---------|---------|---------|
| spec-driven-implementation | ✅ | ✅ | ✅ | ✅ | ✅ |
| python-fastapi-dev | ❌ | ✅ | ✅ | ✅ | ✅ |
| nextjs-app-router-dev | ❌ | ✅ | ✅ | ✅ | ✅ |
| mcp-server-builder | ❌ | ❌ | ✅ | ✅ | ✅ |
| openai-agents-sdk-dev | ❌ | ❌ | ✅ | ✅ | ✅ |
| chatkit-integration | ❌ | ❌ | ✅ | ✅ | ✅ |
| neon-postgres-setup | ❌ | ✅ | ✅ | ✅ | ✅ |
| better-auth-jwt | ❌ | ✅ | ✅ | ✅ | ✅ |
| docker-kubernetes-deployment | ❌ | ❌ | ❌ | ✅ | ✅ |
| kafka-dapr-integration | ❌ | ❌ | ❌ | ❌ | ✅ |
| dapr-sidecar-integration | ❌ | ❌ | ❌ | ❌ | ✅ |
| kafka-event-architecture | ❌ | ❌ | ❌ | ❌ | ✅ |
| cloud-kubernetes-deployment | ❌ | ❌ | ❌ | ❌ | ✅ |
| phase5-orchestration | ❌ | ❌ | ❌ | ❌ | ✅ |

---

## How to Use Skills

### In AGENTS.md:
```markdown
## Available Skills
All AI agents must use these skills when appropriate:

- @.claude/skills/spec-driven-implementation.md (ALWAYS)
- @.claude/skills/python-fastapi-dev.md (Backend)
- @.claude/skills/nextjs-app-router-dev.md (Frontend)
- @.claude/skills/mcp-server-builder.md (AI Tools)
- @.claude/skills/docker-kubernetes-deployment.md (Deployment)
- @.claude/skills/kafka-dapr-integration.md (Events)
```

### In Phase Specs:
```markdown
# Phase 3 Specification

## Required Skills
- spec-driven-implementation
- python-fastapi-dev
- mcp-server-builder
- openai-agents-sdk-dev
- chatkit-integration
```

### With Claude Code:
```bash
# Claude automatically loads skills from .claude/skills/
# Reference them in your prompts:

"Using @.claude/skills/mcp-server-builder.md, implement the add_task MCP tool"
```

---

## Skill Development Workflow

1. **Identify need** - What capability is missing?
2. **Create skill file** - Document patterns and best practices
3. **Test skill** - Use in a small example
4. **Refine skill** - Update based on real usage
5. **Reuse skill** - Apply across multiple phases

---

## Next Steps

1. ✅ Save all provided skills to `.claude/skills/`
2. ⚠️ Create the 4 missing skills listed above
3. ✅ Reference skills in your `AGENTS.md`
4. ✅ Update `constitution.md` to mandate skill usage
5. ✅ Start Phase 1 using `spec-driven-implementation` skill

---

## Skill Quality Checklist

Each skill should have:
- [ ] Clear purpose statement
- [ ] Technologies/stack used
- [ ] Code examples with task references
- [ ] Best practices section
- [ ] Common pitfalls to avoid
- [ ] Integration instructions
- [ ] Testing guidance

---

## Summary

You now have **10 complete skills** and need to create **4 more** for a total of **14 skills** to complete the entire hackathon. These skills will ensure:

✅ Consistent code quality across phases
✅ Reusable knowledge for Claude Code
✅ Faster development (no re-explaining patterns)
✅ Spec-driven approach throughout
✅ Production-ready implementations

Save all skills to `.claude/skills/` and reference them in your specs!