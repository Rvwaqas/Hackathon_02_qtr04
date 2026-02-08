# Skill: Phase V Orchestration

## Purpose
Central coordination and governance for the entire Phase V workflow. Oversee feature implementation, Dapr/Kafka integration, and cloud deployment while ensuring no regressions in Phase III/IV functionality.

## Tech Stack
- **FeatureAgent**: Advanced todo features (priorities, tags, recurring, reminders)
- **DaprAgent**: Distributed runtime integration
- **KafkaAgent**: Event-driven architecture
- **CloudDeployAgent**: Production cloud deployment
- **OrchestratorAgent**: Workflow coordination (this skill)

## Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PHASE V ORCHESTRATION WORKFLOW                        │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      ORCHESTRATOR AGENT                            │  │
│  │  - Reads /specs/ files                                            │  │
│  │  - Enforces execution order                                        │  │
│  │  - Validates each step                                             │  │
│  │  - Generates documentation                                         │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│                                │                                         │
│                                ▼                                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                   STRICT EXECUTION ORDER                         │    │
│  │                                                                  │    │
│  │   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │    │
│  │   │   STEP 1     │    │   STEP 2     │    │   STEP 3     │      │    │
│  │   │ FeatureAgent │───►│  DaprAgent   │───►│ KafkaAgent   │      │    │
│  │   │              │    │              │    │              │      │    │
│  │   │ • Priorities │    │ • Sidecar    │    │ • Topics     │      │    │
│  │   │ • Tags       │    │ • Pub/Sub    │    │ • Schemas    │      │    │
│  │   │ • Recurring  │    │ • State      │    │ • Consumers  │      │    │
│  │   │ • Reminders  │    │ • Jobs API   │    │ • DLQ        │      │    │
│  │   └──────────────┘    └──────────────┘    └──────────────┘      │    │
│  │          │                   │                   │               │    │
│  │          ▼                   ▼                   ▼               │    │
│  │   ┌──────────────────────────────────────────────────────┐      │    │
│  │   │              VALIDATION CHECKPOINTS                   │      │    │
│  │   │  ✓ Success criteria met                               │      │    │
│  │   │  ✓ No Phase III regression                            │      │    │
│  │   │  ✓ No Phase IV regression                             │      │    │
│  │   │  ✓ Integration tests pass                             │      │    │
│  │   └──────────────────────────────────────────────────────┘      │    │
│  │                              │                                   │    │
│  │                              ▼                                   │    │
│  │   ┌──────────────┐                                               │    │
│  │   │   STEP 4     │                                               │    │
│  │   │CloudDeploy   │                                               │    │
│  │   │   Agent      │                                               │    │
│  │   │              │                                               │    │
│  │   │ • DOKS/AKS   │                                               │    │
│  │   │ • Helm deploy│                                               │    │
│  │   │ • Public URL │                                               │    │
│  │   └──────────────┘                                               │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                │                                         │
│                                ▼                                         │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    FINAL DELIVERABLES                              │  │
│  │  - README Phase V section                                          │  │
│  │  - Demo video script (90 seconds)                                  │  │
│  │  - Bonus points documentation                                      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Part 1: Workflow Orchestration Protocol

### 1.1 Execution Order (MANDATORY)

```
╔═══════════════════════════════════════════════════════════════════════╗
║                    STRICT EXECUTION SEQUENCE                           ║
╠═══════════════════════════════════════════════════════════════════════╣
║                                                                        ║
║  1️⃣ FeatureAgent    →  Database schema, API, UI, chatbot updates      ║
║         │                                                              ║
║         ▼                                                              ║
║  2️⃣ DaprAgent       →  Sidecar config, components, event publishing   ║
║         │                                                              ║
║         ▼                                                              ║
║  3️⃣ KafkaAgent      →  Topics, schemas, consumers, Strimzi/Redpanda  ║
║         │                                                              ║
║         ▼                                                              ║
║  4️⃣ CloudDeployAgent →  DOKS cluster, Helm deploy, public URL         ║
║                                                                        ║
║  ⚠️  NEVER skip steps or change order!                                 ║
║  ⚠️  Each step MUST pass validation before next begins                 ║
║                                                                        ║
╚═══════════════════════════════════════════════════════════════════════╝
```

### 1.2 Pre-Flight Checklist

```markdown
## Pre-Flight Checklist (Before Starting Phase V)

### Phase III Baseline
- [ ] AI chatbot responds to natural language commands
- [ ] MCP tools work: add_task, list_tasks, complete_task, delete_task
- [ ] Conversation history persists
- [ ] User isolation works (each user sees only their tasks)

### Phase IV Baseline
- [ ] Docker images build successfully
- [ ] Helm charts deploy to Minikube
- [ ] All pods in Running state
- [ ] Services accessible via port-forward
- [ ] kubectl-ai / kagent tested

### Environment Ready
- [ ] Neon database accessible
- [ ] API keys configured (Gemini/Cohere)
- [ ] doctl authenticated (for cloud deploy)
- [ ] GitHub repo ready (for CI/CD)
```

## Part 2: Agent Delegation Protocol

### 2.1 FeatureAgent Delegation

```markdown
## Delegation to FeatureAgent

### Scope
Implement advanced todo features with backward compatibility

### Tasks
1. Add priority field (high/medium/low enum) to Task model
2. Add tags field (array of strings) to Task model
3. Implement search/filter/sort API endpoints
4. Add recurring task support (daily/weekly/monthly)
5. Add due dates with reminder scheduling
6. Update MCP tools with new parameters
7. Update chatbot instructions for new commands

### Success Criteria
- [ ] Schema migrations run without errors
- [ ] Basic CRUD still works (backward compatible)
- [ ] New endpoints return correct data
- [ ] Chatbot understands: "add high priority task"
- [ ] Chatbot understands: "show tasks tagged work"
- [ ] Chatbot understands: "create daily recurring task"

### Expected Output
- Updated SQLModel models
- New/updated API endpoints
- Updated MCP tool definitions
- Updated chatbot instructions
- Test cases for new features
```

### 2.2 DaprAgent Delegation

```markdown
## Delegation to DaprAgent

### Scope
Add Dapr sidecar integration for event-driven features

### Context from FeatureAgent
- Task model now has: priority, tags, recurring_interval, due_date, remind_before
- New events needed: task.created, task.completed (for recurring), reminder.triggered

### Tasks
1. Create Dapr component YAMLs (pubsub, state, jobs, secrets)
2. Add event publishing code for task CRUD
3. Implement state management for conversation history (via Dapr State API)
4. Schedule reminders using Dapr Jobs API
5. Update Helm charts with Dapr annotations

### Success Criteria
- [ ] Dapr components deploy successfully
- [ ] Events publish to Kafka via localhost:3500
- [ ] State can be read/written via Dapr State API
- [ ] Jobs can be scheduled for future execution
- [ ] Helm charts include dapr.io/enabled annotations

### Expected Output
- dapr-components/*.yaml files
- Event publisher module
- State manager module
- Job scheduler module
- Updated Helm templates
```

### 2.3 KafkaAgent Delegation

```markdown
## Delegation to KafkaAgent

### Scope
Design and implement Kafka event infrastructure

### Context from DaprAgent
- Events will be published via Dapr Pub/Sub
- Need topics for: task lifecycle, reminders, UI updates

### Tasks
1. Define topic configurations (partitions, retention)
2. Create CloudEvents JSON schemas
3. Implement consumer services (Recurring, Notification)
4. Configure Strimzi or Redpanda
5. Set up dead letter queues

### Success Criteria
- [ ] Topics created: task-events, reminders, task-updates
- [ ] Events follow CloudEvents 1.0 format
- [ ] Recurring service creates next occurrence on task.completed
- [ ] Notification service sends alerts on reminder.triggered
- [ ] Failed events go to dead letter topic

### Expected Output
- Topic definitions
- Event schemas (JSON)
- Consumer service code
- Strimzi/Redpanda configuration
- DLQ configuration
```

### 2.4 CloudDeployAgent Delegation

```markdown
## Delegation to CloudDeployAgent

### Scope
Deploy complete application to cloud Kubernetes

### Context from Previous Agents
- Application has Dapr sidecars
- Kafka is required (Strimzi or Redpanda Cloud)
- All features working locally

### Tasks
1. Create DOKS cluster via doctl
2. Install Dapr on cloud cluster
3. Deploy Kafka (Strimzi or connect to Redpanda Cloud)
4. Push Docker images to registry
5. Deploy with Helm using cloud values
6. Configure LoadBalancer for public access
7. Verify all services running

### Success Criteria
- [ ] DOKS cluster created with 2 nodes
- [ ] Dapr control plane running
- [ ] Kafka brokers accessible
- [ ] All pods in Running state
- [ ] Public URL accessible
- [ ] End-to-end flow works (chat → task → event → notification)

### Expected Output
- Cluster creation commands
- Helm value overrides (values-doks.yaml)
- Deployment verification script
- Public URL for demo
```

## Part 3: Validation Framework

### 3.1 Validation Checkpoint Template

```markdown
## Validation Report: [Step Name]

### Status: [PASS / FAIL / PARTIAL]

### Criteria Evaluation

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | [Criterion 1] | ✅/❌ | [How verified] |
| 2 | [Criterion 2] | ✅/❌ | [How verified] |
| 3 | [Criterion 3] | ✅/❌ | [How verified] |

### Phase III Regression Check
- Basic CRUD: [PASS/FAIL]
- Chatbot responses: [PASS/FAIL]
- User isolation: [PASS/FAIL]

### Phase IV Regression Check
- Docker builds: [PASS/FAIL]
- Helm deploy (local): [PASS/FAIL]
- Port-forward access: [PASS/FAIL]

### Issues Found
1. [Issue description and severity]
2. [Issue description and severity]

### Recommendation
[PROCEED / BLOCK / REMEDIATE]

### Next Steps
[What happens next based on recommendation]
```

### 3.2 Regression Testing Checklist

```bash
#!/bin/bash
# regression-tests.sh
# Run after each major Phase V change

echo "═══════════════════════════════════════════════════════════"
echo "PHASE V REGRESSION TEST SUITE"
echo "═══════════════════════════════════════════════════════════"

# Phase III Tests
echo ""
echo "📋 Phase III: AI Chatbot Tests"
echo "───────────────────────────────────────────────────────────"

# Test 1: Basic task creation
echo "Test 1: Create task via chatbot..."
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "add task buy milk"}' \
  | jq '.response' | grep -q "created" && echo "✅ PASS" || echo "❌ FAIL"

# Test 2: List tasks
echo "Test 2: List tasks via chatbot..."
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "show my tasks"}' \
  | jq '.response' | grep -q "milk" && echo "✅ PASS" || echo "❌ FAIL"

# Test 3: Complete task
echo "Test 3: Complete task via chatbot..."
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "complete task 1"}' \
  | jq '.response' | grep -q "completed" && echo "✅ PASS" || echo "❌ FAIL"

# Test 4: User isolation
echo "Test 4: User isolation..."
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "other_user", "message": "show my tasks"}' \
  | jq '.response' | grep -qv "milk" && echo "✅ PASS" || echo "❌ FAIL"

# Phase IV Tests
echo ""
echo "🐳 Phase IV: Container Tests"
echo "───────────────────────────────────────────────────────────"

# Test 5: Docker build
echo "Test 5: Docker build (backend)..."
docker build -t test-backend ./backend > /dev/null 2>&1 && echo "✅ PASS" || echo "❌ FAIL"

# Test 6: Docker build (frontend)
echo "Test 6: Docker build (frontend)..."
docker build -t test-frontend ./frontend > /dev/null 2>&1 && echo "✅ PASS" || echo "❌ FAIL"

# Test 7: Helm lint
echo "Test 7: Helm lint..."
helm lint ./helm/todo-app > /dev/null 2>&1 && echo "✅ PASS" || echo "❌ FAIL"

# Test 8: Helm template
echo "Test 8: Helm template render..."
helm template test ./helm/todo-app > /dev/null 2>&1 && echo "✅ PASS" || echo "❌ FAIL"

# Phase V Tests (if applicable)
echo ""
echo "🚀 Phase V: New Feature Tests"
echo "───────────────────────────────────────────────────────────"

# Test 9: Priority task
echo "Test 9: Create priority task..."
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "add high priority task urgent meeting"}' \
  | jq '.response' | grep -qi "priority\|high\|created" && echo "✅ PASS" || echo "⏭️ SKIP (not implemented yet)"

# Test 10: Tagged task
echo "Test 10: Create tagged task..."
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "test", "message": "add task call mom tag:family"}' \
  | jq '.response' | grep -qi "tag\|family\|created" && echo "✅ PASS" || echo "⏭️ SKIP (not implemented yet)"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "REGRESSION TESTS COMPLETE"
echo "═══════════════════════════════════════════════════════════"
```

## Part 4: Cross-Agent Coordination

### 4.1 Data Flow Between Agents

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CROSS-AGENT DATA FLOW                                 │
│                                                                          │
│  FeatureAgent                                                            │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ OUTPUT:                                                         │     │
│  │ • Task model: id, title, priority, tags, recurring, due_date   │     │
│  │ • API endpoints: GET/POST/PUT/DELETE /tasks with new params    │     │
│  │ • MCP tools: add_task(priority, tags, recurring, due_date)     │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                │                                         │
│                                ▼                                         │
│  DaprAgent                                                               │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ INPUT: Task model schema, API endpoints                         │     │
│  │                                                                 │     │
│  │ OUTPUT:                                                         │     │
│  │ • Event types: task.created, task.updated, task.completed       │     │
│  │ • Event payload: {task_id, user_id, priority, tags, ...}       │     │
│  │ • Dapr endpoints: /v1.0/publish/kafka-pubsub/task-events       │     │
│  │ • State keys: conversation-{user_id}-{conversation_id}         │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                │                                         │
│                                ▼                                         │
│  KafkaAgent                                                              │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ INPUT: Event types, payload schemas, Dapr pubsub config        │     │
│  │                                                                 │     │
│  │ OUTPUT:                                                         │     │
│  │ • Topics: task-events (partition by user_id)                   │     │
│  │ • Schemas: CloudEvents with task data                           │     │
│  │ • Consumers: RecurringService, NotificationService              │     │
│  │ • Strimzi/Redpanda config                                       │     │
│  └────────────────────────────────────────────────────────────────┘     │
│                                │                                         │
│                                ▼                                         │
│  CloudDeployAgent                                                        │
│  ┌────────────────────────────────────────────────────────────────┐     │
│  │ INPUT: All artifacts from previous agents                       │     │
│  │                                                                 │     │
│  │ OUTPUT:                                                         │     │
│  │ • DOKS cluster with Dapr + Kafka                                │     │
│  │ • Deployed pods: frontend, backend, recurring, notification    │     │
│  │ • Public URL: http://<load-balancer-ip>                        │     │
│  └────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Handoff Protocol

```python
"""
Orchestrator handoff protocol
[Task]: Coordinate agent transitions
"""

class AgentHandoff:
    """Standard handoff between agents"""

    def __init__(self, from_agent: str, to_agent: str):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.artifacts = {}
        self.validation_passed = False

    def add_artifact(self, name: str, content: any):
        """Add output artifact from previous agent"""
        self.artifacts[name] = content

    def validate_prerequisites(self) -> bool:
        """Check if handoff can proceed"""
        required = self.get_required_artifacts()
        missing = [r for r in required if r not in self.artifacts]

        if missing:
            print(f"❌ Missing artifacts for {self.to_agent}: {missing}")
            return False

        self.validation_passed = True
        return True

    def get_required_artifacts(self) -> list:
        """Define what each agent needs from predecessor"""
        requirements = {
            "DaprAgent": ["task_model", "api_endpoints", "mcp_tools"],
            "KafkaAgent": ["event_types", "dapr_pubsub_config", "state_schema"],
            "CloudDeployAgent": ["docker_images", "helm_charts", "dapr_components", "kafka_config"]
        }
        return requirements.get(self.to_agent, [])


# Example usage in orchestration
async def orchestrate_phase_v():
    """Main orchestration loop"""

    # Step 1: FeatureAgent
    feature_result = await run_feature_agent()
    handoff_1 = AgentHandoff("FeatureAgent", "DaprAgent")
    handoff_1.add_artifact("task_model", feature_result.model)
    handoff_1.add_artifact("api_endpoints", feature_result.endpoints)
    handoff_1.add_artifact("mcp_tools", feature_result.tools)

    if not handoff_1.validate_prerequisites():
        raise Exception("FeatureAgent did not produce required artifacts")

    # Step 2: DaprAgent
    dapr_result = await run_dapr_agent(handoff_1.artifacts)
    handoff_2 = AgentHandoff("DaprAgent", "KafkaAgent")
    handoff_2.add_artifact("event_types", dapr_result.events)
    handoff_2.add_artifact("dapr_pubsub_config", dapr_result.pubsub)
    handoff_2.add_artifact("state_schema", dapr_result.state)

    if not handoff_2.validate_prerequisites():
        raise Exception("DaprAgent did not produce required artifacts")

    # Continue for KafkaAgent and CloudDeployAgent...
```

## Part 5: Final Documentation Generation

### 5.1 README Phase V Section Template

```markdown
# Phase V: Advanced Features & Cloud Deployment

## Overview
Phase V extends the todo application with advanced features (priorities, tags, recurring tasks, reminders) and deploys to production cloud Kubernetes with event-driven architecture.

## New Features

### Priority Support
Tasks can now have priority levels: `high`, `medium`, `low`
```
"add high priority task: Submit report"
"show high priority tasks"
"sort tasks by priority"
```

### Tags/Categories
Organize tasks with custom tags:
```
"add task call mom tag:family"
"show tasks tagged work"
"add tags shopping,urgent to task 5"
```

### Recurring Tasks
Create tasks that repeat automatically:
```
"create daily task: morning standup"
"add weekly recurring task: team sync"
"make task 3 repeat monthly"
```

### Due Dates & Reminders
Set deadlines with automatic reminders:
```
"add task finish report due tomorrow"
"remind me about task 5 in 2 hours"
"show overdue tasks"
```

## Architecture

### Event-Driven Design
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Backend   │────►│   Kafka     │────►│  Consumers  │
│  (FastAPI)  │     │  (Dapr)     │     │             │
│             │     │             │     │ • Recurring │
│  +Dapr      │     │ • task-evts │     │ • Notifier  │
│  Sidecar    │     │ • reminders │     │             │
└─────────────┘     └─────────────┘     └─────────────┘
```

### Topics
| Topic | Purpose | Consumers |
|-------|---------|-----------|
| `task-events` | Task lifecycle | RecurringService |
| `reminders` | Reminder triggers | NotificationService |
| `task-updates` | Real-time UI | WebSocket Gateway |

## Deployment

### Cloud Infrastructure
- **Platform**: DigitalOcean Kubernetes (DOKS)
- **Nodes**: 2x s-2vcpu-4gb
- **Region**: NYC1

### Access
- **Public URL**: http://[LOAD_BALANCER_IP]
- **API Docs**: http://[LOAD_BALANCER_IP]/api/docs

### Quick Deploy
```bash
# Deploy to cloud
./scripts/deploy-cloud.sh

# Verify
./scripts/verify-deployment.sh
```

## Bonus Points Coverage

| Bonus | Implementation | Evidence |
|-------|----------------|----------|
| **Event-Driven** | Kafka + Dapr Pub/Sub | task-events topic |
| **Dapr Portability** | All infra via sidecar | No direct Kafka client |
| **AIOps** | kubectl-ai for debugging | Deployment docs |
| **CI/CD** | GitHub Actions | .github/workflows/ |

## Demo

### 90-Second Demo Script
See: [docs/demo-script.md](docs/demo-script.md)

### Key Flows to Show
1. Create prioritized task with tags
2. Show Kafka event in logs
3. Complete recurring task → new occurrence created
4. Access via public cloud URL
```

### 5.2 Demo Video Script (90 Seconds)

```markdown
# Phase V Demo Script (90 Seconds)

## Setup (Before Recording)
- Browser tab 1: Cloud URL (frontend)
- Browser tab 2: kubectl logs (Kafka events)
- Terminal: ready for commands

---

## INTRO (0-10 seconds)
"Welcome to Phase V of the AI Todo Chatbot. Today I'll show you advanced features, event-driven architecture, and cloud deployment."

---

## FEATURE DEMO (10-40 seconds)

### Priority & Tags (10-20s)
[Type in chat]
"add high priority task: Submit quarterly report tag:work"

[Explain]
"I can create tasks with priorities and tags. The chatbot understands natural language."

### Show Task List (20-25s)
[Type in chat]
"show my high priority tasks"

[Explain]
"Tasks are filtered by priority. I can also filter by tags."

### Recurring Task (25-35s)
[Type in chat]
"create daily recurring task: Morning standup"

[Explain]
"Recurring tasks will automatically create the next occurrence when completed."

### Complete to Trigger (35-40s)
[Type in chat]
"complete task 1"

[Explain]
"Watch the Kafka logs..."

---

## EVENT DEMO (40-60 seconds)

### Show Kafka Events (40-50s)
[Switch to kubectl logs tab]

"Here you can see the task.completed event was published to Kafka via Dapr."

[Highlight]
- Event type: com.taskmanager.task.completed
- Topic: task-events
- Partition key: user_id

### Show New Occurrence (50-60s)
[Switch back to frontend]

[Type in chat]
"show my tasks"

[Explain]
"The RecurringService consumed the event and created tomorrow's occurrence automatically. This is event-driven architecture in action."

---

## CLOUD DEMO (60-80 seconds)

### Show Public URL (60-70s)
[Point to browser URL bar]

"This is running on DigitalOcean Kubernetes. The URL is publicly accessible."

### Show kubectl (70-80s)
[Terminal command]
```
kubectl get pods -n todo-app
```

[Explain]
"2 replicas of frontend, 2 of backend, all with Dapr sidecars. Production-ready."

---

## WRAP UP (80-90 seconds)

"To summarize Phase V:
- Advanced features: priorities, tags, recurring, reminders
- Event-driven with Kafka and Dapr
- Deployed to cloud Kubernetes
- Fully production-ready

Thank you!"

---

## END
```

## Part 6: Bonus Points Alignment

### 6.1 Bonus Points Checklist

```markdown
## Hackathon Bonus Points Alignment

### 1. Event-Driven Architecture ✅
- [ ] Kafka/Redpanda for message streaming
- [ ] CloudEvents format for all events
- [ ] Multiple consumer services
- [ ] Dead letter queue for failed events
- [ ] Idempotent event processing

**Evidence**:
- `task-events` topic with task lifecycle
- `reminders` topic with notification triggers
- RecurringService and NotificationService consumers

### 2. Dapr Portability ✅
- [ ] All infrastructure access via Dapr sidecar
- [ ] No direct Kafka/Redis/DB clients in code
- [ ] Swappable component configurations
- [ ] State management via Dapr State API
- [ ] Secrets via Dapr Secrets API

**Evidence**:
- `httpx.post("http://localhost:3500/v1.0/publish/...")`
- No `kafka-python`, `aiokafka`, `confluent-kafka` imports
- Component YAMLs support Strimzi AND Redpanda

### 3. AIOps Integration ✅
- [ ] kubectl-ai for natural language K8s operations
- [ ] kagent for cluster health analysis
- [ ] Gordon AI for Dockerfile optimization (optional)
- [ ] AI-assisted troubleshooting

**Evidence**:
- kubectl-ai commands in deployment docs
- kagent health check scripts
- Troubleshooting guide with AI assistance

### 4. CI/CD Pipeline ✅
- [ ] GitHub Actions workflow
- [ ] Automated Docker build
- [ ] Automated Helm deploy
- [ ] Environment-specific configurations
- [ ] Rollback capability

**Evidence**:
- `.github/workflows/deploy-cloud.yaml`
- Multi-stage builds for efficiency
- Separate values files per environment

### 5. Documentation ✅
- [ ] README with all phases
- [ ] API documentation
- [ ] Deployment guide
- [ ] Architecture diagrams
- [ ] Demo video script

**Evidence**:
- README.md with Phase V section
- API_DOCUMENTATION.md
- DEPLOYMENT_GUIDE.md
- Architecture diagrams in docs/
```

## Part 7: Risk Assessment

### 7.1 Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Cloud credit expiry** | Medium | High | Monitor usage, set alerts, cleanup unused resources |
| **API rate limits** | Medium | Medium | Implement caching, retry with backoff |
| **Kafka broker failure** | Low | High | 3 broker HA, replication factor 3 |
| **Dapr sidecar crash** | Low | High | Health checks, auto-restart, logging |
| **Cost overrun** | Medium | Medium | Use smallest instances, cleanup script |
| **Demo failure** | Low | High | Pre-record backup, local fallback |

### 7.2 Cost Monitoring

```bash
#!/bin/bash
# cost-monitor.sh

echo "═══════════════════════════════════════════════════════════"
echo "CLOUD COST MONITOR"
echo "═══════════════════════════════════════════════════════════"

# DigitalOcean
echo ""
echo "📊 DigitalOcean Usage"
echo "───────────────────────────────────────────────────────────"
doctl balance get 2>/dev/null || echo "doctl not configured"

# Estimate
echo ""
echo "📈 Estimated Monthly Cost"
echo "───────────────────────────────────────────────────────────"
echo "DOKS Cluster (2 nodes):     \$24/month"
echo "Load Balancer:              \$12/month"
echo "Block Storage (20GB):       \$2/month"
echo "Container Registry:         Free (500MB)"
echo "───────────────────────────────────────────────────────────"
echo "Total:                      ~\$38/month"
echo ""
echo "Free credit remaining: Check DO dashboard"

# Cleanup recommendations
echo ""
echo "💡 Cost Saving Tips"
echo "───────────────────────────────────────────────────────────"
echo "• Delete cluster when not demoing"
echo "• Use Redpanda Cloud (free) instead of self-hosted Kafka"
echo "• Use Neon free tier for PostgreSQL"
echo "• Set budget alerts in DO dashboard"
```

## Part 8: Progress Tracking

### 8.1 Orchestration Status Template

```markdown
## Phase V Orchestration Status

### Overall Progress
[████████░░] 80% Complete

### Step Status

| Step | Agent | Status | Started | Completed | Notes |
|------|-------|--------|---------|-----------|-------|
| 1 | FeatureAgent | ✅ Complete | 2024-01-15 | 2024-01-15 | All features working |
| 2 | DaprAgent | ✅ Complete | 2024-01-15 | 2024-01-16 | Components deployed |
| 3 | KafkaAgent | 🔄 In Progress | 2024-01-16 | - | Setting up consumers |
| 4 | CloudDeployAgent | ⏳ Pending | - | - | Waiting for Step 3 |

### Current Blockers
- None

### Risks Identified
1. Kafka topic creation taking longer than expected
2. Need to verify Redpanda Cloud credentials

### Next Actions
1. Complete KafkaAgent consumer implementation
2. Run regression tests
3. Begin CloudDeployAgent work

### Estimated Completion
- KafkaAgent: Today
- CloudDeployAgent: Tomorrow
- Full Phase V: 2 days
```

## Summary

| Component | Purpose |
|-----------|---------|
| **Execution Order** | FeatureAgent → DaprAgent → KafkaAgent → CloudDeployAgent |
| **Validation** | Checkpoints after each agent, regression tests |
| **Coordination** | Handoff protocol with required artifacts |
| **Documentation** | README section, demo script, bonus points |
| **Risk Management** | Cost monitoring, credit tracking, mitigation plans |

### Quick Reference

```bash
# Run regression tests
./scripts/regression-tests.sh

# Check orchestration status
cat docs/orchestration-status.md

# Generate demo script
cat docs/demo-script.md

# Verify bonus points
cat docs/bonus-points-checklist.md
```
