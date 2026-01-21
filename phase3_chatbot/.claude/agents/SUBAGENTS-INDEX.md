# Subagents Index - Hackathon II

## Overview
This document lists all 6 specialized subagents for the Hackathon II project. Each subagent is an expert in a specific domain and can be invoked by the main development agent or used directly through OpenAI Agents SDK handoffs.

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

## The 6 Subagents

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

You now have **6 specialized subagents** that work together:

1. **Spec Architect** - Writes specifications
2. **Backend Builder** - Builds FastAPI backends
3. **Frontend Builder** - Builds Next.js frontends
4. **AI Agent Builder** - Adds AI features
5. **Cloud Ops Engineer** - Handles deployment
6. **Test Writer** - Ensures quality

These subagents integrate via **OpenAI Agents SDK handoffs** and can be orchestrated by a main agent for complete end-to-end development workflows.

**Ready to start building!** 🚀