# Implementation Plan: Local Kubernetes Deployment

**Branch**: `004-local-k8s-deployment` | **Date**: 2026-01-23 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-local-k8s-deployment/spec.md`

## Summary

Deploy the complete AI-Powered Todo Chatbot (Phase III) as a cloud-native system on local Kubernetes using Minikube and Helm Charts. This involves optimizing existing Docker images for size targets (<100MB frontend, <200MB backend), creating a unified Helm chart for both services, deploying to Minikube, and demonstrating extensive AIOps usage through Gordon, kubectl-ai, and kagent tools.

## Technical Context

**Language/Version**: Python 3.11 (Backend), Node.js 18 (Frontend)
**Primary Dependencies**: FastAPI, Cohere API, Next.js 15, Better Auth
**Storage**: External Neon PostgreSQL (connection via Kubernetes Secret)
**Testing**: Manual verification via health endpoints and UI flow
**Target Platform**: Local Minikube cluster on Docker Desktop (Windows)
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Pods healthy within 2 minutes, UI loads within 10 seconds
**Constraints**: CPU ≤ 2 cores/pod, Memory ≤ 1GB/pod, combined image size < 300MB
**Scale/Scope**: Single replica deployment for local development/demonstration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Strictly Spec-Driven Development | ✅ PASS | Plan derived from spec.md; all tasks traceable |
| II. AI-Assisted Operations Only | ✅ WILL COMPLY | Gordon for Docker, kubectl-ai/kagent for Helm/K8s |
| III. Backward Compatibility | ✅ WILL VERIFY | Test all Phase III features post-deployment |
| IV. Reusable Blueprints | ✅ PLANNED | Helm chart parameterized for Phase V reuse |
| V. Demonstrable AIOps | ✅ PLANNED | Document all AI commands in README |
| VI. Tech Stack Standardization | ✅ COMPLIANT | Docker Desktop, Minikube, Helm as specified |

**Non-Negotiables Compliance**:
- [x] No manual docker/kubectl/helm without AI assistance
- [x] Secrets via Helm secrets (not hardcoded)
- [x] Every action traceable to spec/plan/tasks
- [x] Phase III functionality preserved
- [x] Gordon usage documented
- [x] Final demo shows chatbot in Minikube

## Project Structure

### Documentation (this feature)

```text
specs/004-local-k8s-deployment/
├── spec.md              # Feature specification (completed)
├── plan.md              # This file
├── checklists/
│   └── requirements.md  # Specification checklist (completed)
└── tasks.md             # Implementation tasks (next: /sp.tasks)
```

### Source Code (repository root)

```text
# Phase III existing structure (source for containerization)
../phase3_chatbot/
├── backend/
│   ├── src/
│   │   ├── main.py            # FastAPI entry point
│   │   ├── models/            # SQLAlchemy models
│   │   ├── services/          # Business logic + Cohere agent
│   │   └── routers/           # API endpoints
│   └── requirements.txt
└── frontend/
    ├── src/
    │   ├── app/               # Next.js app directory
    │   ├── components/        # React components
    │   └── lib/               # Utilities
    ├── package.json
    └── next.config.js

# Phase IV new artifacts (to be created)
phase4_chatbot/
├── docker/
│   ├── Dockerfile.backend     # Optimized multi-stage Dockerfile
│   └── Dockerfile.frontend    # Optimized standalone Dockerfile
├── helm/
│   └── todo-chatbot/          # Helm chart directory
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── templates/
│       │   ├── _helpers.tpl
│       │   ├── backend-deployment.yaml
│       │   ├── backend-service.yaml
│       │   ├── frontend-deployment.yaml
│       │   ├── frontend-service.yaml
│       │   ├── configmap.yaml
│       │   └── secret.yaml
│       └── .helmignore
├── scripts/
│   ├── build-images.sh        # Gordon-assisted image build script
│   ├── deploy.sh              # Full deployment script
│   └── verify.sh              # Verification script
└── README.md                  # Deployment guide with AI commands
```

**Structure Decision**: Web application pattern with separate frontend/backend containers, unified Helm chart, external database (Neon). Dockerfiles placed in `docker/` directory to avoid conflicts with Phase III Dockerfiles.

## Implementation Phases

### Phase 1: Docker Image Optimization (P1 from Spec)

**Goal**: Create optimized Docker images meeting size targets

**Tasks**:
1. **Backend Dockerfile Optimization**
   - Use multi-stage build with Python 3.11-slim
   - Gordon AI prompt: "Optimize this Dockerfile for FastAPI with Cohere, target <200MB"
   - Add health check endpoint verification
   - Expected size: < 200MB

2. **Frontend Dockerfile Optimization**
   - Use Next.js standalone output mode
   - Gordon AI prompt: "Create minimal Next.js 15 standalone Dockerfile, target <100MB"
   - Configure for alpine base with minimal dependencies
   - Expected size: < 100MB

3. **Local Docker Verification**
   - Run `docker build` with Gordon assistance
   - Test with `docker run` and environment variables
   - Verify health endpoints respond
   - Document image sizes

**Exit Criteria**:
- [ ] Backend image builds and runs locally
- [ ] Frontend image builds and runs locally
- [ ] Combined size < 300MB
- [ ] Health endpoints return 200 OK
- [ ] Gordon prompts documented

### Phase 2: Helm Chart Creation (P2 from Spec)

**Goal**: Create validated Helm chart for Kubernetes deployment

**Tasks**:
1. **Chart Scaffolding**
   - kubectl-ai command: "Create Helm chart scaffold for two-service web app"
   - Initialize Chart.yaml with metadata
   - Set up values.yaml with defaults

2. **Backend Templates**
   - kubectl-ai command: "Generate deployment template for FastAPI backend with health probes"
   - Create Deployment with resource limits
   - Create Service (ClusterIP)
   - Configure environment from ConfigMap/Secret

3. **Frontend Templates**
   - kubectl-ai command: "Generate deployment template for Next.js frontend"
   - Create Deployment with resource limits
   - Create Service (NodePort for minikube access)
   - Configure API URL environment variable

4. **Configuration Resources**
   - Create ConfigMap for non-sensitive config
   - Create Secret template for:
     - DATABASE_URL
     - COHERE_API_KEY
     - JWT_SECRET
   - Use helm template functions for base64 encoding

5. **Chart Validation**
   - Run `helm lint todo-chatbot/`
   - Run `helm template todo-chatbot/`
   - Run `helm install --dry-run --debug`
   - Fix any errors/warnings

**Exit Criteria**:
- [ ] `helm lint` passes with zero errors
- [ ] `helm template` generates valid manifests
- [ ] `helm install --dry-run` succeeds
- [ ] kubectl-ai commands documented

### Phase 3: Minikube Deployment (P3 from Spec)

**Goal**: Successfully deploy and access application on Minikube

**Tasks**:
1. **Minikube Setup**
   - Start Minikube with adequate resources: `minikube start --cpus=4 --memory=8192`
   - Enable necessary addons
   - Configure Docker environment: `eval $(minikube docker-env)`

2. **Image Build in Minikube**
   - Build images inside Minikube Docker daemon
   - Tag appropriately for local use
   - Verify images are available: `docker images`

3. **Secret Creation**
   - Create Kubernetes secret with actual values:
     ```
     kubectl create secret generic todo-chatbot-secrets \
       --from-literal=database-url=<NEON_URL> \
       --from-literal=cohere-api-key=<KEY> \
       --from-literal=jwt-secret=<SECRET>
     ```

4. **Helm Install**
   - Run: `helm install todo-chatbot ./helm/todo-chatbot`
   - Monitor pod startup: `kubectl get pods -w`
   - Check events: `kubectl get events --sort-by=.lastTimestamp`

5. **Service Access**
   - Get frontend URL: `minikube service todo-chatbot-frontend --url`
   - Verify URL is accessible in browser
   - Test backend health: `curl <backend-service>/health`

6. **Troubleshooting (if needed)**
   - kagent command: "Analyze pod health and suggest fixes"
   - Check logs: `kubectl logs <pod-name>`
   - Describe pods: `kubectl describe pod <pod-name>`

**Exit Criteria**:
- [ ] Both pods in Running state
- [ ] No pod restarts (CrashLoopBackOff)
- [ ] Frontend accessible via minikube service URL
- [ ] Backend health endpoint returns 200
- [ ] kagent analysis documented

### Phase 4: Functionality Verification (P4 from Spec)

**Goal**: Confirm all Phase III features work in Kubernetes environment

**Tasks**:
1. **Authentication Flow**
   - Create new account via signup form
   - Login with created credentials
   - Verify JWT token handling
   - Test logout functionality

2. **Task Management**
   - Create task via dashboard
   - View task list
   - Update task status
   - Delete task
   - Verify immediate UI updates

3. **Chatbot Interaction**
   - Open chatbot interface
   - Ask: "Add a task called 'Test from Kubernetes'"
   - Verify Cohere agent processes request
   - Confirm task appears in dashboard
   - Test conversation history

4. **Data Persistence**
   - Note current tasks
   - Delete backend pod: `kubectl delete pod <backend-pod>`
   - Wait for pod recreation
   - Verify tasks and conversation persist (Neon DB)

5. **User Isolation**
   - Create second user account
   - Verify first user's tasks not visible
   - Create task as second user
   - Switch back, confirm isolation

**Exit Criteria**:
- [ ] Signup/Login works
- [ ] CRUD operations complete successfully
- [ ] Chatbot creates tasks via natural language
- [ ] Data persists across pod restarts
- [ ] User isolation verified

### Phase 5: AIOps Documentation (P5 from Spec)

**Goal**: Document AI-assisted operations for hackathon bonus points

**Tasks**:
1. **Gordon Documentation**
   - Capture all Gordon prompts used for Dockerfiles
   - Include Gordon's responses/suggestions
   - Document any optimizations applied
   - Screenshot or log evidence

2. **kubectl-ai Documentation**
   - List all kubectl-ai commands used
   - Capture generated YAML outputs
   - Document any debugging commands
   - Include scaling demonstrations

3. **kagent Documentation**
   - Capture health analysis commands
   - Document optimization suggestions
   - Include troubleshooting examples
   - Show resource utilization reports

4. **README Creation**
   - Write deployment guide with exact commands
   - Include prerequisites section
   - Document all environment variables
   - Add troubleshooting section
   - Embed AI command evidence

5. **Agent Coordination Evidence**
   - Document how BlueprintAgent orchestrated workflow
   - Show DockerAgent → HelmAgent → K8sAgent progression
   - Capture any multi-agent interactions

**Exit Criteria**:
- [ ] At least 3 Gordon prompts documented
- [ ] At least 3 kubectl-ai commands documented
- [ ] At least 2 kagent commands documented
- [ ] README complete with deployment steps
- [ ] Agent roles visible in documentation

## Risk Analysis

| Risk | Impact | Mitigation |
|------|--------|------------|
| Gordon unavailable on Windows | High | Fallback to standard Dockerfile; document limitation |
| Minikube resource exhaustion | Medium | Set conservative limits; monitor with `kubectl top` |
| Neon DB connection issues | High | Test connection before deployment; verify SSL config |
| Image size exceeds targets | Low | Iterate with Gordon suggestions; accept reasonable variance |

## Dependencies

**External Services**:
- Neon PostgreSQL (existing from Phase III)
- Cohere API (key required)

**Local Tools Required**:
- Docker Desktop with Gordon enabled
- Minikube CLI installed
- Helm CLI installed
- kubectl-ai and kagent installed

**Phase III Artifacts**:
- Working frontend source code
- Working backend source code
- Valid API keys and database URL

## Success Metrics

From spec SC-001 through SC-010:

| Metric | Target | Verification |
|--------|--------|--------------|
| Image build time | < 5 min each | Timed build |
| Combined image size | < 300MB | `docker images` |
| helm lint | 0 errors | Command output |
| Pod startup time | < 2 min | `kubectl get pods` timestamps |
| UI load time | < 10 seconds | Browser test |
| E2E flow completion | < 5 min | Manual walkthrough |
| Pod restart persistence | Data intact | Verify after `kubectl delete pod` |
| AIOps documentation | 3/3/2 commands | README review |
| Full deployment time | < 15 min | Timed from clean state |

## Next Steps

1. Run `/sp.tasks` to generate detailed implementation tasks
2. Begin Phase 1 (Docker optimization) with Gordon AI
3. Progress through phases sequentially
4. Create PHR after each major milestone
5. Final demo preparation
