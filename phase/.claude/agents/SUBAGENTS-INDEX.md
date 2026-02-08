# Subagents Index - Hackathon II

## Overview
This document lists all 15 specialized subagents for the Hackathon II project. Each subagent is an expert in a specific domain and can be invoked by the main development agent or used directly through OpenAI Agents SDK handoffs.

### Agent Categories
- **Core Development (1-6)**: Spec writing, backend, frontend, AI features, deployment, testing
- **Infrastructure (7-10)**: Docker, Helm, K8s, Blueprint orchestration
- **Phase V (11-15)**: Advanced features, Dapr, Kafka, Cloud deploy, Orchestration

---

## What are Subagents?

Subagents are specialized AI agents that handle specific aspects of development. Using OpenAI Agents SDK, they can be invoked in two ways:

### 1. As Tools (agent.as_tool())
```python
# Subagent exposed as a tool
customer_agent = Agent(
    name="Customer Service",
    instructions="...",
    tools=[
        spec_architect.as_tool(
            tool_name="spec_expert",
            tool_description="Creates specifications"
        )
    ]
)
```

### 2. As Handoffs (handoffs=[agent])
```python
# Main agent can delegate to subagents
main_agent = Agent(
    name="Main Developer",
    instructions="Coordinate development",
    handoffs=[
        spec_architect,
        backend_builder,
        frontend_builder,
        ai_agent_builder,
        cloud_ops_engineer,
        test_writer
    ]
)
```

---

## The 15 Subagents

### 1. **Spec Architect** 📋
**File**: `.claude/subagents/spec_architect.py`

**Purpose**: Expert in writing specifications and breaking down requirements.

**Responsibilities**:
- Write `specify.md` (WHAT to build)
- Write `plan.md` (HOW to build)
- Write `tasks.md` (BREAKDOWN implementation)
- Validate specifications
- Ensure cross-phase consistency

**When to Use**:
- Starting any new phase
- Adding new features
- Refining requirements
- Breaking down complex features

**Skills Used**:
- `spec-driven-implementation.md`

**Tools Available**:
- `validate_specification`: Check completeness
- `check_phase_consistency`: Ensure alignment

**Example Usage**:
```python
result = await Runner.run(
    spec_architect,
    "Create specifications for Phase 3: AI Chatbot"
)
```

---

### 2. **Backend Builder** ⚙️
**File**: `.claude/subagents/backend_builder.py`

**Purpose**: Expert in FastAPI backend development.

**Responsibilities**:
- Implement FastAPI applications
- Create SQLModel database models
- Add JWT authentication
- Build MCP servers
- Write async/await code

**When to Use**:
- Implementing any backend functionality
- Creating API endpoints
- Database operations
- Authentication implementation

**Skills Used**:
- `python-fastapi-dev.md`
- `neon-postgres-setup.md`
- `better-auth-jwt.md`
- `mcp-server-builder.md`

**Tools Available**:
- `analyze_api_endpoint`: Check REST design
- `generate_sqlmodel_schema`: Create models
- `check_async_patterns`: Validate async code

**Example Usage**:
```python
result = await Runner.run(
    backend_builder,
    "Implement Phase 2 backend with REST API and JWT auth"
)
```

---

### 3. **Frontend Builder** 🎨
**File**: `.claude/subagents/frontend_builder.py`

**Purpose**: Expert in Next.js frontend development.

**Responsibilities**:
- Build Next.js App Router pages
- Create Server/Client Components
- Implement Better Auth flows
- Style with Tailwind CSS
- Build type-safe API clients

**When to Use**:
- Implementing UI components
- Creating pages and layouts
- Authentication flows
- ChatKit integration

**Skills Used**:
- `nextjs-app-router-dev.md`
- `better-auth-jwt.md`
- `chatkit-integration.md`

**Tools Available**:
- `analyze_component_type`: Server vs Client
- `suggest_tailwind_classes`: Get styling suggestions
- `check_typescript_types`: Validate types

**Example Usage**:
```python
result = await Runner.run(
    frontend_builder,
    "Implement Phase 2 frontend with authentication and task management UI"
)
```

---

### 4. **AI Agent Builder** 🤖
**File**: `.claude/subagents/ai_agent_builder.py`

**Purpose**: Expert in building AI-powered features.

**Responsibilities**:
- Build OpenAI Agents SDK implementations
- Create MCP servers
- Implement stateless chat architecture
- Integrate ChatKit
- Design conversational flows

**When to Use**:
- Phase 3+ AI features
- Building chatbots
- MCP tool creation
- Natural language interfaces

**Skills Used**:
- `openai-agents-sdk-dev.md`
- `mcp-server-builder.md`
- `chatkit-integration.md`

**Tools Available**:
- `validate_mcp_tool`: Check MCP tool definitions
- `analyze_agent_instructions`: Improve agent instructions

**Example Usage**:
```python
result = await Runner.run(
    ai_agent_builder,
    "Implement Phase 3: AI chatbot with MCP tools for task management"
)
```

---

### 5. **Cloud Ops Engineer** ☁️
**File**: `.claude/subagents/cloud_ops_engineer.py`

**Purpose**: Expert in containerization and cloud deployment.

**Responsibilities**:
- Create Dockerfiles
- Build Helm charts
- Deploy to Kubernetes
- Set up Kafka
- Configure Dapr
- Use kubectl-ai/kagent

**When to Use**:
- Phase 4-5 deployment tasks
- Containerization
- Kubernetes setup
- Event-driven architecture
- Production deployment

**Skills Used**:
- `docker-kubernetes-deployment.md`
- `kafka-dapr-integration.md`

**Tools Available**:
- `validate_dockerfile`: Check Docker best practices
- `check_k8s_resources`: Validate K8s configs
- `suggest_dapr_component`: Get Dapr recommendations

**Example Usage**:
```python
result = await Runner.run(
    cloud_ops_engineer,
    "Implement Phase 4: Deploy to Kubernetes with Helm charts"
)
```

---

### 7. **Docker Agent** 🐳
**File**: `.claude/agents/docker-agent.md`

**Purpose**: Elite containerization architect for advanced Docker tasks.

**Responsibilities**:
- Multi-stage Dockerfile generation (Next.js standalone, FastAPI with uv)
- Image size optimization (<100MB frontend, <200MB backend)
- Gordon AI prompt crafting for intelligent Dockerfile generation
- .dockerignore file creation for faster builds
- Multi-platform builds (amd64/arm64)
- Security scanning with Trivy
- Dockerfile linting with Hadolint
- Debug common build errors (caching, permissions)

**When to Use**:
- Creating optimized Dockerfiles
- Image size reduction tasks
- Multi-platform build setup
- Security scanning integration
- Docker build debugging
- Gordon AI Dockerfile generation

**Skills Used**:
- `docker-kubernetes-deployment.md`
- Gordon AI integration

**Capabilities**:
| Capability | Description |
|------------|-------------|
| **Next.js Optimization** | Standalone output, node:20-alpine, <100MB target |
| **FastAPI with uv** | uv sync, python:3.12-slim, <200MB target |
| **Gordon AI** | Craft optimized prompts for Dockerfile generation |
| **Multi-Platform** | docker buildx for amd64/arm64 |
| **Security Scanning** | Trivy integration for vulnerability detection |
| **Linting** | Hadolint best practices enforcement |
| **Debugging** | Layer caching, permission issues, context size |

**Example Usage**:
```python
result = await Runner.run(
    docker_agent,
    "Create an optimized Dockerfile for my Next.js app - under 100MB"
)
```

```python
result = await Runner.run(
    docker_agent,
    "Build multi-platform images for amd64 and arm64"
)
```

```python
result = await Runner.run(
    docker_agent,
    "Use Gordon AI to generate a FastAPI Dockerfile with uv"
)
```

---

### 8. **Helm Agent** ⎈
**File**: `.claude/agents/helm-agent.md`

**Purpose**: Elite Kubernetes packaging architect for Helm chart development.

**Responsibilities**:
- Complete Helm chart scaffolding (Chart.yaml, values.yaml, templates/)
- AI-assisted template generation via kubectl-ai prompts
- kagent for values.yaml and resource optimization
- Deployment, Service, ConfigMap, Secret templates
- Environment-specific values files (values-local.yaml, values-prod.yaml)
- Secret management (Sealed Secrets, External Secrets Operator)
- Helm hooks for migrations and init containers
- Dependency management with subcharts
- Validation (helm lint, helm template, helm install --dry-run)
- Upgrade strategies and rollback plans

**When to Use**:
- Creating new Helm charts
- Packaging applications for Kubernetes
- Multi-environment deployments
- Secret management in K8s
- AI-assisted resource generation
- Helm chart debugging and validation

**Skills Used**:
- `docker-kubernetes-deployment.md`
- kubectl-ai / kagent integration

**Capabilities**:
| Capability | Description |
|------------|-------------|
| **Chart Scaffolding** | Complete structure with all standard files |
| **kubectl-ai** | AI prompts for Deployment, Service, Ingress, HPA |
| **kagent** | Values optimization and resource tuning |
| **Multi-Environment** | values-local, values-staging, values-prod |
| **Secret Management** | Sealed Secrets, External Secrets Operator |
| **Helm Hooks** | Pre-install/upgrade migrations, init containers |
| **Dependencies** | Subchart management (PostgreSQL, Redis, etc.) |
| **Validation** | lint, template, dry-run, API deprecation checks |
| **Rollback** | Safe upgrade and rollback strategies |

**Example Usage**:
```python
result = await Runner.run(
    helm_agent,
    "Create a Helm chart for my FastAPI backend with PostgreSQL dependency"
)
```

```python
result = await Runner.run(
    helm_agent,
    "Use kubectl-ai to generate optimized deployment templates"
)
```

```python
result = await Runner.run(
    helm_agent,
    "Set up Sealed Secrets for my production deployment"
)
```

---

### 9. **K8s Agent** ☸️
**File**: `.claude/agents/k8s-agent.md`

**Purpose**: Elite Kubernetes operations specialist for cluster management and troubleshooting.

**Responsibilities**:
- Minikube cluster management (start, stop, delete, dashboard)
- kubectl-ai for natural language Kubernetes operations
- kagent for cluster health analysis and resource optimization
- Deploy, scale, expose, logs, describe, debug operations
- Port-forwarding and minikube service URL access
- Pod troubleshooting (CrashLoopBackOff, OOM, ImagePull errors)
- Log aggregation and tailing
- Resource requests/limits tuning for local machine
- Namespace management
- Cleanup commands and verification scripts

**When to Use**:
- Managing Minikube clusters
- Natural language K8s operations (kubectl-ai)
- Cluster health analysis (kagent)
- Pod troubleshooting and debugging
- Accessing services via port-forward
- Resource optimization
- Cleanup and verification

**Skills Used**:
- `docker-kubernetes-deployment.md`
- kubectl-ai / kagent integration

**Capabilities**:
| Capability | Description |
|------------|-------------|
| **Minikube** | start/stop/delete with custom resources, dashboard |
| **kubectl-ai** | Natural language deploy, scale, expose, debug |
| **kagent** | Cluster health analysis, resource optimization |
| **Port-Forward** | Quick service access, minikube service --url |
| **Troubleshooting** | CrashLoopBackOff, OOM, ImagePull diagnosis |
| **Logging** | Aggregation, tailing, stern/kubetail |
| **Resources** | Requests/limits tuning for local machines |
| **Namespaces** | Create, manage, quota |
| **Cleanup** | helm uninstall, kubectl delete, minikube delete |
| **Verification** | Wait for pods, curl health checks, scripts |

**Example Usage**:
```python
result = await Runner.run(
    k8s_agent,
    "Start Minikube with 4GB memory and enable dashboard"
)
```

```python
result = await Runner.run(
    k8s_agent,
    "My pods are in CrashLoopBackOff, help me debug"
)
```

```python
result = await Runner.run(
    k8s_agent,
    "Use kagent to analyze cluster health and suggest optimizations"
)
```

```python
result = await Runner.run(
    k8s_agent,
    "Set up port-forwarding to access my backend service"
)
```

---

### 10. **Blueprint Agent** 🗺️
**File**: `.claude/agents/blueprint-agent.md`

**Purpose**: Elite infrastructure orchestration architect for spec-driven deployments.

**Responsibilities**:
- Full orchestration of DockerAgent → HelmAgent → K8sAgent
- Extract infrastructure requirements from /specs/
- Success criteria validation at each deployment phase
- Automatic documentation generation (README, deployment docs)
- Reusable blueprint pattern creation
- Risk assessment and mitigation suggestions
- End-to-end flow coordination
- Final deployment report with lessons learned
- Alignment with Spec-Driven Infrastructure Automation
- Bonus points documentation (AIOps usage, agent coordination)

**When to Use**:
- Full spec-to-deployment workflows
- Infrastructure artifact generation from specs
- Multi-agent deployment orchestration
- Deployment documentation generation
- Hackathon submission preparation
- Risk assessment for deployments

**Skills Used**:
- All infrastructure skills (Docker, Helm, K8s)
- Spec-Driven Development (SDD)
- AIOps integration

**Capabilities**:
| Capability | Description |
|------------|-------------|
| **Orchestration** | DockerAgent → HelmAgent → K8sAgent flow |
| **Spec Parsing** | Extract requirements from /specs/ |
| **Validation** | Success criteria checks per phase |
| **Documentation** | README sections, deployment guides |
| **Blueprints** | Reusable deployment patterns |
| **Risk Assessment** | Identify and mitigate risks |
| **AIOps Docs** | Gordon AI, kubectl-ai, kagent usage |
| **Reports** | Final deployment reports with metrics |
| **Bonus Points** | Agent coordination documentation |

**Orchestration Flow:**
```
┌─────────────────────────────────────────┐
│         BLUEPRINT ORCHESTRATION          │
├─────────────────────────────────────────┤
│  1. Spec Analysis                        │
│     └── Extract requirements             │
│              ▼                           │
│  2. Docker Phase (DockerAgent)           │
│     └── ✓ Validate images                │
│              ▼                           │
│  3. Helm Phase (HelmAgent)               │
│     └── ✓ Validate charts                │
│              ▼                           │
│  4. K8s Phase (K8sAgent)                 │
│     └── ✓ Validate deployment            │
│              ▼                           │
│  5. Documentation & Report               │
│     └── Generate all artifacts           │
└─────────────────────────────────────────┘
```

**Example Usage**:
```python
result = await Runner.run(
    blueprint_agent,
    "Deploy my application from specs/chatbot to Minikube"
)
```

```python
result = await Runner.run(
    blueprint_agent,
    "Generate all infrastructure artifacts from the finalized spec"
)
```

```python
result = await Runner.run(
    blueprint_agent,
    "Create deployment documentation with bonus points coverage"
)
```

```python
result = await Runner.run(
    blueprint_agent,
    "Validate our deployment matches the specifications"
)
```

---

### 11. **Feature Agent** 🎯
**File**: `.claude/agents/feature-agent.md`

**Purpose**: Specialist for implementing intermediate and advanced todo features using spec-driven development.

**Responsibilities**:
- Extend task model with priorities, tags, search/filter/sort, recurring tasks, due dates
- Update database schema first (SQLModel models + migrations)
- Extend MCP tools with new parameters
- Update Cohere agent instructions for new commands
- Maintain backward compatibility
- Add UI components (dropdowns, tags input, date pickers)

**When to Use**:
- Adding priority levels to tasks
- Implementing tags/categories
- Building search, filter, sort features
- Adding recurring task functionality
- Implementing due dates and reminders

**Feature Domains**:
| Feature | Description |
|---------|-------------|
| **Priorities** | high/medium/low enum, sorting, visual indicators |
| **Tags/Categories** | Array of strings, autocomplete, filtering |
| **Search/Filter/Sort** | Full-text search, multi-criteria filtering |
| **Recurring Tasks** | Daily/weekly/monthly intervals, auto-regeneration |
| **Due Dates & Reminders** | DateTime field, scheduling, timezone handling |

**Example Usage**:
```python
result = await Runner.run(
    feature_agent,
    "Add priority support (high/medium/low) to tasks"
)
```

---

### 12. **Dapr Integration Agent** 🔌
**File**: `.claude/agents/dapr-integration-agent.md`

**Purpose**: Master architect for Dapr (Distributed Application Runtime) configuration and integration.

**Responsibilities**:
- Add Dapr sidecars and components to applications
- Configure pub/sub messaging with Kafka
- Set up state management with PostgreSQL
- Implement job scheduling via Dapr Jobs API
- Configure secrets management
- Enable service-to-service invocation

**When to Use**:
- Adding event-driven messaging
- Distributed state management
- Service mesh integration
- Secrets management via Dapr
- Replacing direct infrastructure clients with Dapr abstraction

**Dapr Building Blocks**:
| Block | Component Type | Use Case |
|-------|---------------|----------|
| **Pub/Sub** | pubsub.kafka | Event-driven messaging |
| **State** | state.postgresql | Distributed state storage |
| **Jobs** | Jobs API | Scheduled/recurring jobs |
| **Secrets** | Various | Secure secret retrieval |
| **Invocation** | Service-to-service | Built-in resiliency |

**Rule**: All application-to-infrastructure communication MUST go through Dapr sidecar (`localhost:3500`).

**Example Usage**:
```python
result = await Runner.run(
    dapr_agent,
    "Configure Dapr pub/sub for task event publishing"
)
```

---

### 13. **Kafka Event Architect** 📨
**File**: `.claude/agents/kafka-event-architect.md`

**Purpose**: Elite specialist in event-driven architecture with Kafka, Redpanda, and Strimzi.

**Responsibilities**:
- Design Kafka topics and partitioning strategies
- Create event schemas (CloudEvents format)
- Implement producer/consumer patterns via Dapr Pub/Sub
- Provide platform recommendations (Redpanda Cloud vs Strimzi)
- Configure consumer service subscriptions

**When to Use**:
- Designing messaging infrastructure
- Creating event schemas for task CRUD
- Setting up notification event consumers
- Choosing between Kafka deployment options
- Publishing events for recurring tasks

**Standard Topics**:
| Topic | Purpose |
|-------|---------|
| `task-events` | Task lifecycle (created, updated, deleted, completed) |
| `reminders` | Reminder scheduling and triggers |
| `task-updates` | Real-time task modification notifications |

**Platform Recommendations**:
- **Cloud**: Redpanda Cloud (serverless, pay-per-use)
- **Self-hosted**: Strimzi operator (full control, GitOps)

**Example Usage**:
```python
result = await Runner.run(
    kafka_agent,
    "Design event schemas for task CRUD operations"
)
```

---

### 14. **Cloud Deploy Agent** ☁️
**File**: `.claude/agents/cloud-deploy-agent.md`

**Purpose**: Expert in production-grade Kubernetes deployment on major cloud providers.

**Responsibilities**:
- Deploy to DOKS (DigitalOcean), AKS (Azure), GKE (Google)
- Create cloud-specific Helm value overrides
- Configure Dapr and Kafka on cloud clusters
- Set up load balancers, ingress, external-dns
- Handle secrets management with cloud-native stores
- Implement HA patterns (replicas, PDBs, HPA)

**When to Use**:
- Deploying to cloud Kubernetes
- Creating cloud-specific configurations
- Setting up production infrastructure
- Configuring HA and autoscaling
- Managing multi-cloud deployments

**Cloud-Specific Capabilities**:
| Provider | Load Balancer | Secrets | Registry |
|----------|--------------|---------|----------|
| **DOKS** | DO LB | DO Secrets | DO Container Registry |
| **AKS** | Azure LB | Key Vault | ACR |
| **GKE** | Google Cloud LB | Secret Manager | GCR/Artifact Registry |

**Recommendation**: Prefer DOKS for $200 free credit offering.

**Example Usage**:
```python
result = await Runner.run(
    cloud_deploy_agent,
    "Deploy application to DigitalOcean Kubernetes"
)
```

---

### 15. **Orchestrator Agent** 🎭
**File**: `.claude/agents/orchestrator-agent.md`

**Purpose**: Central coordinator for Phase V workflow, functioning as the master agent for the entire pipeline.

**Responsibilities**:
- Read and analyze specs from `/specs/` directory
- Enforce strict execution order of agents
- Delegate to specialized agents with scoped instructions
- Validate completion at each workflow step
- Ensure no regression in Phase III/IV functionality
- Generate comprehensive Phase V documentation

**When to Use**:
- Starting Phase V implementation
- Checking Phase V progress status
- Coordinating multi-agent workflows
- Validating backward compatibility
- Generating final README sections

**Execution Order (MANDATORY)**:
```
FeatureAgent → DaprAgent → KafkaAgent → CloudDeployAgent
```

**Validation Framework**:
| Check | Description |
|-------|-------------|
| **Success Criteria** | Specs requirements are met |
| **Phase III Regression** | Core functionality intact |
| **Phase IV Regression** | Local K8s deployment intact |
| **Integration Points** | Components properly connected |
| **Tests** | All tests pass |

**Example Usage**:
```python
result = await Runner.run(
    orchestrator_agent,
    "Start Phase V implementation with spec analysis"
)
```

---

### 6. **Test Writer** 🧪
**File**: `.claude/subagents/test_writer.py`

**Purpose**: Expert in comprehensive testing.

**Responsibilities**:
- Write pytest tests (backend)
- Write Jest tests (frontend)
- Validate acceptance criteria
- Achieve test coverage
- Write integration tests

**When to Use**:
- After implementing features
- Validating acceptance criteria
- Ensuring code quality
- Before deployment

**Skills Used**:
- Testing best practices
- pytest and Jest frameworks

**Tools Available**:
- `generate_test_cases_from_acceptance_criteria`: Get test ideas
- `analyze_test_coverage`: Check completeness

**Example Usage**:
```python
result = await Runner.run(
    test_writer,
    "Write tests for Phase 2 backend API endpoints"
)
```

---

## Subagent Workflow

### Typical Development Flow

```
1. User Request
   ↓
2. Main Agent receives request
   ↓
3. Main Agent determines which subagent(s) needed
   ↓
4. Handoff to Spec Architect (if new feature)
   → Creates specifications
   ↓
5. Handoff to Backend Builder
   → Implements API
   ↓
6. Handoff to Frontend Builder
   → Implements UI
   ↓
7. Handoff to AI Agent Builder (if Phase 3+)
   → Adds AI features
   ↓
8. Handoff to Cloud Ops Engineer (if Phase 4+)
   → Deploys to K8s
   ↓
9. Handoff to Test Writer
   → Validates with tests
   ↓
10. Return to Main Agent
    → Delivers complete feature
```

---

## Integration Pattern

### Creating Main Orchestrator Agent

```python
"""
main_orchestrator.py - Main development agent
"""

from agents import Agent
from subagents.spec_architect import spec_architect
from subagents.backend_builder import backend_builder
from subagents.frontend_builder import frontend_builder
from subagents.ai_agent_builder import ai_agent_builder
from subagents.cloud_ops_engineer import cloud_ops_engineer
from subagents.test_writer import test_writer

# Main orchestrator that can delegate to all subagents
main_agent = Agent(
    name="Main Developer",
    instructions="""
    You are the Main Developer orchestrating the Hackathon II project.
    
    Your role is to coordinate between specialized subagents:
    
    1. **Spec Architect** - For specifications (specify, plan, tasks)
    2. **Backend Builder** - For FastAPI backend implementation
    3. **Frontend Builder** - For Next.js frontend implementation
    4. **AI Agent Builder** - For AI/MCP features (Phase 3+)
    5. **Cloud Ops Engineer** - For deployment (Phase 4+)
    6. **Test Writer** - For testing and validation
    
    Workflow:
    1. Understand user request
    2. Determine which phase and features needed
    3. Delegate to appropriate subagent(s)
    4. Coordinate between subagents
    5. Ensure quality and completion
    
    Always follow Spec-Driven Development:
    - Specifications first (Spec Architect)
    - Implementation next (Backend/Frontend/AI Builders)
    - Testing last (Test Writer)
    - Deployment when ready (Cloud Ops Engineer)
    """,
    handoffs=[
        spec_architect,
        backend_builder,
        frontend_builder,
        ai_agent_builder,
        cloud_ops_engineer,
        test_writer
    ]
)
```

### Using the Main Agent

```python
from agents import Runner
import asyncio

async def develop_feature(request: str):
    """
    Main entry point for development requests.
    Main agent automatically delegates to subagents.
    """
    result = await Runner.run(main_agent, request)
    return result.final_output

# Examples
asyncio.run(develop_feature("Start Phase 2: Build full-stack web app"))
asyncio.run(develop_feature("Add AI chatbot feature"))
asyncio.run(develop_feature("Deploy to Kubernetes"))
```

---

## Subagent Usage by Phase

| Phase | Spec Architect | Backend Builder | Frontend Builder | AI Agent Builder | Cloud Ops | Test Writer |
|-------|---------------|-----------------|------------------|------------------|-----------|-------------|
| **Phase 1** | ✅ Required | ❌ | ❌ | ❌ | ❌ | ✅ Optional |
| **Phase 2** | ✅ Required | ✅ Required | ✅ Required | ❌ | ❌ | ✅ Required |
| **Phase 3** | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ❌ | ✅ Required |
| **Phase 4** | ✅ Optional | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ✅ Required |
| **Phase 5** | ✅ Optional | ✅ Required | ✅ Required | ✅ Required | ✅ Required | ✅ Required |

---

## Benefits of Subagents

### 1. **Specialization**
Each subagent is an expert in its domain with deep knowledge of best practices.

### 2. **Modularity**
Subagents can be used independently or combined for complex tasks.

### 3. **Consistency**
Using the same subagents ensures consistent code quality across phases.

### 4. **Scalability**
Main agent can delegate work to multiple subagents simultaneously (future enhancement).

### 5. **Maintainability**
Changes to a specific domain (e.g., backend patterns) only affect one subagent.

### 6. **Quality Assurance**
Built-in validation tools ensure specifications and code meet standards.

---

## Best Practices

### 1. Always Start with Spec Architect
```python
# ✅ CORRECT
result = await Runner.run(main_agent, "Start Phase 3")
# Main agent delegates to Spec Architect first
# Then to implementation subagents

# ❌ WRONG - Skipping specifications
result = await Runner.run(backend_builder, "Build Phase 3")
# No specs to follow!
```

### 2. Use Appropriate Subagent for Task
```python
# ✅ CORRECT - Right subagent for task
await Runner.run(backend_builder, "Create REST API")
await Runner.run(frontend_builder, "Create UI component")

# ❌ WRONG - Wrong subagent
await Runner.run(frontend_builder, "Create database model")
# Frontend Builder doesn't handle backend!
```

### 3. Validate with Test Writer
```python
# ✅ CORRECT - Test after implementation
await Runner.run(backend_builder, "Implement feature")
await Runner.run(test_writer, "Test the feature")

# ❌ WRONG - No testing
await Runner.run(backend_builder, "Implement feature")
# How do you know it works?
```

---

## Troubleshooting

### Issue: Subagent Not Following Specs

**Solution**: Ensure specifications exist and are referenced:
```python
prompt = """
Implement feature X according to:
- specs/phase2/specify.md §3.2
- specs/phase2/plan.md §4.1
- specs/phase2/tasks.md T-014
"""
```

### Issue: Subagents Working in Silos

**Solution**: Use main orchestrator agent to coordinate:
```python
# Let main agent coordinate
await Runner.run(
    main_agent,
    "Implement Phase 3 with backend, frontend, and AI features"
)
# Main agent handles handoffs between subagents
```

### Issue: Inconsistent Code Quality

**Solution**: Ensure subagents reference their skills:
```python
# Skills are automatically loaded from .claude/skills/
# Subagents reference them in their instructions
```

---

## Next Steps

1. ✅ Save all 6 subagents to `.claude/subagents/`
2. ✅ Create main orchestrator agent
3. ✅ Test each subagent individually
4. ✅ Test orchestration flow
5. ✅ Start Phase 1 implementation

---

## Summary

You now have **15 specialized subagents** that work together:

### Core Development Agents (1-6)
1. **Spec Architect** - Writes specifications
2. **Backend Builder** - Builds FastAPI backends
3. **Frontend Builder** - Builds Next.js frontends
4. **AI Agent Builder** - Adds AI features
5. **Cloud Ops Engineer** - Handles deployment
6. **Test Writer** - Ensures quality

### Infrastructure Agents (7-10)
7. **Docker Agent** - Elite containerization (multi-stage, optimization, Gordon AI, multi-platform, security)
8. **Helm Agent** - Kubernetes packaging (charts, kubectl-ai, kagent, secrets, multi-env, rollback)
9. **K8s Agent** - Cluster operations (Minikube, kubectl-ai, kagent, troubleshooting, port-forward, cleanup)
10. **Blueprint Agent** - Infrastructure orchestration (Docker→Helm→K8s, spec-driven, validation, documentation)

### Phase V Agents (11-15)
11. **Feature Agent** - Advanced todo features (priorities, tags, search/filter, recurring tasks, due dates)
12. **Dapr Integration Agent** - Distributed Application Runtime (pub/sub, state, jobs, secrets, invocation)
13. **Kafka Event Architect** - Event-driven architecture (topics, schemas, CloudEvents, Redpanda/Strimzi)
14. **Cloud Deploy Agent** - Cloud K8s deployment (DOKS, AKS, GKE, HA patterns, autoscaling)
15. **Orchestrator Agent** - Phase V coordinator (workflow enforcement, validation, documentation)

### Phase V Workflow
```
FeatureAgent → DaprAgent → KafkaAgent → CloudDeployAgent
     ↑                                          ↑
     └──────── Orchestrated by OrchestratorAgent ────┘
```

These subagents integrate via **OpenAI Agents SDK handoffs** and can be orchestrated by a main agent for complete end-to-end development workflows.

**Ready to start building!** 🚀