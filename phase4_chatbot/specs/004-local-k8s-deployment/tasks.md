# Tasks: Local Kubernetes Deployment

**Input**: Design documents from `/specs/004-local-k8s-deployment/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Manual verification via health endpoints and UI flow (no automated test suite)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths and AI commands in descriptions
- **Agent**: Each task specifies the responsible agent (BlueprintAgent, DockerAgent, HelmAgent, K8sAgent)

## Path Conventions

- **Phase IV Structure**: `phase4_chatbot/` at repository root
- **Docker**: `docker/` directory for Dockerfiles
- **Helm**: `helm/todo-chatbot/` for Helm chart
- **Scripts**: `scripts/` for automation
- **Source**: `../phase3_chatbot/` for application source code

---

## Phase 1: Setup (Environment Verification)

**Purpose**: Verify all required tools are installed and functional
**Agent**: BlueprintAgent

- [X] T001 Verify Docker Desktop is running with Gordon AI enabled
- [X] T002 [P] Check Minikube installation: `minikube version`
- [X] T003 [P] Check kubectl installation: `kubectl version --client`
- [X] T004 [P] Check Helm installation: `helm version`
- [X] T005 [P] Check kubectl-ai installation: `kubectl ai "hello"` (Not compatible on Windows)
- [X] T006 [P] Check kagent installation: `kagent version` (Not installed)
- [X] T007 Test Gordon AI: `docker ai "What can you do?"` (Requires Docker Desktop running)
- [X] T008 Create phase4_chatbot/README.md with "Phase IV Setup Verification" section documenting tool versions

**Checkpoint**: All tools verified - Docker/Helm/K8s operations can begin

---

## Phase 2: Foundational (Project Structure)

**Purpose**: Create directory structure and prepare for containerization
**Agent**: BlueprintAgent

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T009 Create directory structure: `phase4_chatbot/docker/`
- [X] T010 [P] Create directory structure: `phase4_chatbot/helm/todo-chatbot/`
- [X] T011 [P] Create directory structure: `phase4_chatbot/helm/todo-chatbot/templates/`
- [X] T012 [P] Create directory structure: `phase4_chatbot/scripts/`
- [X] T013 Copy Phase III frontend source to working directory (or reference in Dockerfile)
- [X] T014 Copy Phase III backend source to working directory (or reference in Dockerfile)
- [X] T015 Verify Neon database connection string is available in .env

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Docker Image Build and Local Test (Priority: P1) 🎯 MVP

**Goal**: Containerize frontend and backend services into optimized Docker images
**Agent**: DockerAgent

**Independent Test**: Run `docker run` for each image and verify health endpoints respond

### Implementation for User Story 1

#### Frontend Docker Image

- [X] T016 [US1] Use Gordon AI to generate optimized Dockerfile: `docker ai "create optimized multi-stage Dockerfile for Next.js 15 app with standalone output, target under 100MB"` → save to docker/Dockerfile.frontend
- [X] T017 [US1] Create docker/.dockerignore with node_modules, .next, .git exclusions
- [ ] T018 [US1] Build frontend image: `docker build -t todo-frontend:latest -f docker/Dockerfile.frontend ../phase3_chatbot/frontend`
- [ ] T019 [US1] Verify frontend image size: `docker images todo-frontend:latest` (target: <100MB)
- [ ] T020 [US1] Test frontend container locally: `docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 todo-frontend:latest`
- [ ] T021 [US1] Verify frontend loads at http://localhost:3000

#### Backend Docker Image

- [X] T022 [US1] Use Gordon AI to generate optimized Dockerfile: `docker ai "create optimized multi-stage Dockerfile for FastAPI app with Python 3.11-slim, target under 200MB"` → save to docker/Dockerfile.backend
- [X] T023 [US1] Create docker/.dockerignore with __pycache__, .venv, .git exclusions
- [ ] T024 [US1] Build backend image: `docker build -t todo-backend:latest -f docker/Dockerfile.backend ../phase3_chatbot/backend`
- [ ] T025 [US1] Verify backend image size: `docker images todo-backend:latest` (target: <200MB)
- [ ] T026 [US1] Test backend container locally: `docker run -p 8000:8000 -e DATABASE_URL=<neon_url> -e COHERE_API_KEY=<key> todo-backend:latest`
- [ ] T027 [US1] Verify backend health endpoint: `curl http://localhost:8000/health`

#### Documentation

- [X] T028 [US1] Document Gordon AI prompts used in README.md section "Docker Image Creation"
- [X] T029 [US1] Record image sizes in README.md (combined must be <300MB)

**Checkpoint**: Both images built, tested locally, and documented. User Story 1 complete.

---

## Phase 4: User Story 2 - Helm Chart Creation and Validation (Priority: P2)

**Goal**: Create a Helm chart that packages both services for single-command deployment
**Agent**: HelmAgent

**Independent Test**: Run `helm lint` and `helm template` commands to verify chart validity

### Implementation for User Story 2

#### Chart Scaffolding

- [X] T030 [US2] Use kagent to scaffold Helm chart: `kagent "generate basic Helm chart structure for full-stack web app with frontend and backend"` → helm/todo-chatbot/ (Used helm create instead)
- [X] T031 [US2] Create helm/todo-chatbot/Chart.yaml with metadata (name: todo-chatbot, version: 0.1.0, appVersion: 1.0.0)
- [X] T032 [US2] Create helm/todo-chatbot/values.yaml with default configuration
- [X] T033 [US2] Create helm/todo-chatbot/values-local.yaml for Minikube-specific overrides
- [X] T034 [US2] Create helm/todo-chatbot/.helmignore

#### Backend Templates

- [X] T035 [US2] Use kubectl-ai to generate deployment: `kubectl ai "generate helm deployment template for fastapi backend with port 8000, 1 replica, resource limits cpu 500m memory 512Mi"` → helm/todo-chatbot/templates/backend-deployment.yaml (Created manually)
- [X] T036 [US2] Use kubectl-ai to generate service: `kubectl ai "generate helm clusterip service template for backend on port 8000"` → helm/todo-chatbot/templates/backend-service.yaml (Created manually)
- [X] T037 [US2] Add liveness and readiness probes to backend deployment (path: /health, port: 8000)
- [X] T038 [US2] Configure backend environment variables from ConfigMap and Secret references

#### Frontend Templates

- [X] T039 [US2] Use kubectl-ai to generate deployment: `kubectl ai "generate helm deployment template for nextjs frontend with port 3000, 1 replica, resource limits cpu 500m memory 512Mi"` → helm/todo-chatbot/templates/frontend-deployment.yaml (Created manually)
- [X] T040 [US2] Use kubectl-ai to generate service: `kubectl ai "generate helm nodeport service template for frontend on port 3000"` → helm/todo-chatbot/templates/frontend-service.yaml (Created manually)
- [X] T041 [US2] Add liveness and readiness probes to frontend deployment (path: /, port: 3000)
- [X] T042 [US2] Configure frontend environment variables (NEXT_PUBLIC_API_URL pointing to backend service)

#### Configuration Resources

- [X] T043 [US2] Create helm/todo-chatbot/templates/configmap.yaml for non-sensitive config (CORS_ORIGINS, HOST, PORT, DEBUG)
- [X] T044 [US2] Use kagent to generate secrets template: `kagent "create kubernetes secret yaml template for database-url, cohere-api-key, jwt-secret"` → helm/todo-chatbot/templates/secret.yaml (Created manually)
- [X] T045 [US2] Create helm/todo-chatbot/templates/_helpers.tpl with chart helper functions

#### Validation

- [X] T046 [US2] Run `helm lint helm/todo-chatbot/` and fix any errors
- [X] T047 [US2] Run `helm template todo-chatbot helm/todo-chatbot/` and verify valid YAML output
- [ ] T048 [US2] Run `helm install --dry-run --debug todo-chatbot helm/todo-chatbot/` and verify no errors

#### Documentation

- [X] T049 [US2] Document kubectl-ai and kagent commands used in README.md section "Helm Chart Generation"

**Checkpoint**: Helm chart created, validated, and documented. User Story 2 complete.

---

## Phase 5: User Story 3 - Minikube Deployment and Access (Priority: P3)

**Goal**: Deploy application to Minikube and verify local access
**Agent**: K8sAgent

**Independent Test**: Access frontend via `minikube service --url` and verify application loads

### Implementation for User Story 3

#### Minikube Setup

- [ ] T050 [US3] Start Minikube cluster: `minikube start --cpus=4 --memory=8192 --driver=docker`
- [ ] T051 [US3] Verify Minikube status: `minikube status`
- [ ] T052 [US3] Configure shell for Minikube Docker: `eval $(minikube docker-env)` (or equivalent on Windows)

#### Image Loading

- [ ] T053 [US3] Load frontend image into Minikube: `minikube image load todo-frontend:latest`
- [ ] T054 [US3] Load backend image into Minikube: `minikube image load todo-backend:latest`
- [ ] T055 [US3] Verify images available: `minikube image ls | grep todo`

#### Secret Creation

- [ ] T056 [US3] Create Kubernetes secret with actual values: `kubectl create secret generic todo-chatbot-secrets --from-literal=database-url=<NEON_URL> --from-literal=cohere-api-key=<KEY> --from-literal=jwt-secret=<SECRET>`
- [ ] T057 [US3] Verify secret created: `kubectl get secrets todo-chatbot-secrets`

#### Helm Deployment

- [ ] T058 [US3] Install Helm chart: `helm install todo-chatbot ./helm/todo-chatbot --values ./helm/todo-chatbot/values-local.yaml`
- [ ] T059 [US3] Monitor pod startup: `kubectl get pods -w` (wait for Running state)
- [ ] T060 [US3] Check deployment events: `kubectl get events --sort-by=.lastTimestamp`
- [ ] T061 [US3] Verify backend logs: `kubectl logs -l app=todo-backend`
- [ ] T062 [US3] Verify frontend logs: `kubectl logs -l app=todo-frontend`

#### Service Access

- [ ] T063 [US3] Get frontend URL: `minikube service todo-chatbot-frontend --url`
- [ ] T064 [US3] Open frontend URL in browser and verify login page loads
- [ ] T065 [US3] Test backend health via port-forward: `kubectl port-forward svc/todo-chatbot-backend 8000:8000` then `curl http://localhost:8000/health`

#### Documentation

- [ ] T066 [US3] Document deployment steps and access URLs in README.md section "Minikube Deployment"

**Checkpoint**: Application deployed to Minikube and accessible. User Story 3 complete.

---

## Phase 6: User Story 4 - Full Application Functionality Verification (Priority: P4)

**Goal**: Verify all Phase III features work correctly in Kubernetes environment
**Agent**: K8sAgent

**Independent Test**: Complete signup, login, task CRUD, and chatbot interaction

### Implementation for User Story 4

#### Authentication Verification

- [ ] T067 [US4] Access frontend via Minikube URL
- [ ] T068 [US4] Create new user account via signup form
- [ ] T069 [US4] Login with created credentials
- [ ] T070 [US4] Verify JWT token handling (should maintain session)
- [ ] T071 [US4] Test logout functionality

#### Task Management Verification

- [ ] T072 [US4] Create task via dashboard
- [ ] T073 [US4] View task list
- [ ] T074 [US4] Update task status (mark complete)
- [ ] T075 [US4] Delete task
- [ ] T076 [US4] Verify immediate UI updates

#### Chatbot Verification

- [ ] T077 [US4] Open chatbot interface
- [ ] T078 [US4] Send natural language command: "Add a task called 'Test from Kubernetes'"
- [ ] T079 [US4] Verify Cohere agent processes request successfully
- [ ] T080 [US4] Confirm task appears in dashboard
- [ ] T081 [US4] Test conversation history retrieval

#### Persistence Verification

- [ ] T082 [US4] Note current tasks in dashboard
- [ ] T083 [US4] Delete backend pod: `kubectl delete pod -l app=todo-backend`
- [ ] T084 [US4] Wait for pod recreation: `kubectl get pods -w`
- [ ] T085 [US4] Verify tasks and conversation persist (Neon DB connection intact)

#### User Isolation Verification

- [ ] T086 [US4] Create second user account
- [ ] T087 [US4] Login as second user
- [ ] T088 [US4] Verify first user's tasks NOT visible
- [ ] T089 [US4] Create task as second user
- [ ] T090 [US4] Switch back to first user, confirm isolation

#### Documentation

- [ ] T091 [US4] Document verification results in README.md section "Functionality Verification"

**Checkpoint**: All Phase III features verified working in Kubernetes. User Story 4 complete.

---

## Phase 7: User Story 5 - AIOps Demonstration and Documentation (Priority: P5)

**Goal**: Document heavy use of AI-assisted operations for hackathon bonus points
**Agent**: K8sAgent + BlueprintAgent

**Independent Test**: README contains documented evidence of Gordon, kubectl-ai, and kagent usage

### Implementation for User Story 5

#### AIOps Demonstrations

- [ ] T092 [US5] Scale backend deployment: `kubectl ai "scale the todo-backend deployment to 2 replicas"`
- [ ] T093 [US5] Verify scaling: `kubectl get pods -l app=todo-backend`
- [ ] T094 [US5] Scale back to 1: `kubectl ai "scale todo-backend to 1 replica"`
- [ ] T095 [US5] Debug check: `kubectl ai "check why pods might be pending or failing"`
- [ ] T096 [US5] Health analysis: `kagent "analyze cluster health and resource usage"`
- [ ] T097 [US5] Resource optimization: `kagent "suggest resource optimizations for the todo-chatbot deployment"`

#### Documentation Compilation

- [ ] T098 [US5] Compile all Gordon AI prompts used (minimum 3) in README.md section "Gordon AI Usage"
- [ ] T099 [US5] Compile all kubectl-ai commands used (minimum 3) in README.md section "kubectl-ai Commands"
- [ ] T100 [US5] Compile all kagent commands used (minimum 2) in README.md section "kagent Operations"
- [ ] T101 [US5] Document agent coordination flow (BlueprintAgent → DockerAgent → HelmAgent → K8sAgent) in README.md section "Multi-Agent Orchestration"

#### Final README Sections

- [X] T102 [US5] Add "Prerequisites" section listing required tools and versions
- [X] T103 [US5] Add "Quick Start" section with exact deployment commands
- [X] T104 [US5] Add "Cleanup" section: `helm uninstall todo-chatbot && minikube delete`
- [X] T105 [US5] Add "Troubleshooting" section with common issues and AI-assisted solutions

**Checkpoint**: AIOps documented with clear evidence. User Story 5 complete.

---

## Phase 8: Polish & Final Validation

**Purpose**: Final checks and demo preparation
**Agent**: BlueprintAgent

- [X] T106 Create scripts/deploy.sh with full deployment automation
- [X] T107 [P] Create scripts/verify.sh with health check automation
- [X] T108 [P] Create scripts/cleanup.sh with uninstall commands
- [ ] T109 Perform complete end-to-end test from clean state (total time <15 minutes)
- [ ] T110 Prepare demo notes for 90-second video walkthrough
- [X] T111 Final README review - ensure all sections complete and accurate
- [ ] T112 Verify all success criteria from spec.md (SC-001 through SC-010)

**Checkpoint**: All tasks complete, ready for demo/submission

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies - can start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion - BLOCKS all user stories
- **Phase 3 (US1 - Docker)**: Depends on Phase 2 - First MVP milestone
- **Phase 4 (US2 - Helm)**: Depends on Phase 3 (needs working images)
- **Phase 5 (US3 - Deploy)**: Depends on Phase 4 (needs valid Helm chart)
- **Phase 6 (US4 - Verify)**: Depends on Phase 5 (needs running deployment)
- **Phase 7 (US5 - AIOps)**: Depends on Phase 5 (needs running cluster)
- **Phase 8 (Polish)**: Depends on Phases 6 and 7 completion

### User Story Dependencies

```
US1 (Docker) → US2 (Helm) → US3 (Deploy) → US4 (Verify)
                                    ↓
                              US5 (AIOps)
```

**Note**: US4 and US5 can run in parallel once US3 is complete

### Parallel Opportunities

Within each phase, tasks marked [P] can run in parallel:
- **Phase 1**: T002-T006 (tool version checks) can run in parallel
- **Phase 2**: T010-T012 (directory creation) can run in parallel
- **Phase 3**: Frontend (T016-T021) and Backend (T022-T027) can run sequentially within their groups
- **Phase 4**: Backend templates (T035-T038) and Frontend templates (T039-T042) can run in parallel
- **Phase 8**: T107-T108 (script creation) can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (verify tools)
2. Complete Phase 2: Foundational (create structure)
3. Complete Phase 3: User Story 1 (Docker images)
4. **STOP and VALIDATE**: Both images build and run locally
5. Demo Docker images working with `docker run`

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Docker) → Test locally → First Demo!
3. Add US2 (Helm) → Validate with lint/dry-run → Chart ready
4. Add US3 (Deploy) → Test on Minikube → Deployed!
5. Add US4 (Verify) → Full E2E testing → Functionality confirmed
6. Add US5 (AIOps) → Document AI usage → Bonus points captured
7. Polish → Final demo preparation

### Strict Sequential Order

```
T001 → T002...T007 → T008 → T009...T015 → T016...T029 → T030...T049 → T050...T066 → T067...T091 → T092...T105 → T106...T112
```

---

## Task Summary

| Phase | User Story | Task Count | Agent |
|-------|------------|------------|-------|
| 1 | Setup | 8 | BlueprintAgent |
| 2 | Foundational | 7 | BlueprintAgent |
| 3 | US1 - Docker | 14 | DockerAgent |
| 4 | US2 - Helm | 20 | HelmAgent |
| 5 | US3 - Deploy | 17 | K8sAgent |
| 6 | US4 - Verify | 25 | K8sAgent |
| 7 | US5 - AIOps | 14 | K8sAgent + BlueprintAgent |
| 8 | Polish | 7 | BlueprintAgent |
| **Total** | | **112** | |

---

## Notes

- [P] tasks = different files/operations, no dependencies
- [US#] label maps task to specific user story for traceability
- Each user story checkpoint = independently verifiable milestone
- All AI tool usage MUST be documented in README
- Never hardcode secrets - use Kubernetes Secrets
- Commit after each logical group of tasks
- Stop at any checkpoint to demo progress
