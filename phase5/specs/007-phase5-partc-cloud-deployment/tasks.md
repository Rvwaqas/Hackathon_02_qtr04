# Tasks: Phase V Part C - Cloud Deployment on Oracle OKE

**Input**: Design documents from `/specs/007-phase5-partc-cloud-deployment/`
**Prerequisites**: plan.md (required), spec.md (required), quickstart.md, contracts/

**Tests**: Infrastructure validation only (kubectl, dapr, helm commands). No new unit tests — all verification via CLI commands and manual E2E.

**Organization**: Tasks grouped by user story to enable independent implementation and testing. Tasks T-701 through T-712 map to plan phases 0-8.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Exact file paths included in descriptions

---

## Phase 1: Research & Prerequisites (Shared Infrastructure)

**Purpose**: Verify cloud accounts, CLI tools, and research ARM64/OKE requirements before any infrastructure changes.

- [ ] T-701 [US1] Verify Oracle Cloud Always Free account is active and OKE service is available — confirm via OCI Console that tenancy has Kubernetes (OKE) service enabled and Always Free shapes (VM.Standard.A1.Flex) are available in the selected region
- [ ] T-701a [P] [US1] Install and configure OCI CLI locally — run `oci setup config`, verify with `oci iam region list`
- [ ] T-701b [P] [US2] Verify Redpanda Cloud account is active and free tier serverless cluster is available at redpanda.com/cloud
- [x] T-701c [P] [US1] Verify Docker buildx is available locally — run `docker buildx version` and `docker buildx ls` to confirm multi-platform builder support
- [x] T-701d [P] [US1] Verify Helm 3.x installed — run `helm version` (must be 3.x+)
- [x] T-701e [P] [US1] Verify kubectl installed — run `kubectl version --client`

**Checkpoint**: All prerequisites confirmed. Cloud accounts active, CLI tools ready.

---

## Phase 2: User Story 1 — Cloud Cluster Setup & App Deployment (Priority: P1) MVP

**Goal**: Create OKE cluster, install Dapr, update Helm chart for cloud, build multi-arch Docker images, deploy application with public LoadBalancer access.

**Independent Test**: Navigate to LoadBalancer IP in browser → login page loads → login → dashboard → chatbot command returns valid response.

### T-702: Create OKE Cluster & Configure kubectl [US1]

- [ ] T-702a [US1] Create OKE cluster via OCI Console — Quick Create, name: `todo-chatbot-cluster`, K8s 1.28+, shape VM.Standard.A1.Flex, 2 nodes (2 OCPU + 12GB each)
- [ ] T-702b [US1] Download kubeconfig — run `oci ce cluster create-kubeconfig --cluster-id <CLUSTER_OCID> --file $HOME/.kube/config --region <REGION> --token-version 2.0.0`
- [ ] T-702c [US1] Verify kubectl connectivity — `kubectl get nodes` shows 2 Ready nodes with ARM64 architecture

### T-703: Install Dapr on OKE [US1]

- [ ] T-703a [US1] Install Dapr on OKE cluster — `dapr init -k --wait`
- [ ] T-703b [US1] Verify Dapr health — `dapr status -k` shows all system components healthy (operator, sidecar-injector, placement, sentry)
- [ ] T-703c [US1] Verify Dapr pods — `kubectl get pods -n dapr-system` all Running

**Gate**: OKE cluster running, kubectl connected, Dapr healthy.

### T-705: Helm Chart Cloud Extensions [US1]

- [x] T-705a [US1] Update Dapr pubsub template for conditional SASL auth in `helm/todo-chatbot/templates/dapr/pubsub-kafka.yaml` — add `{{- if .Values.kafka.external }}` block with SASL/SCRAM-SHA-256 config, secretKeyRef for kafka-secrets, authType=password, disableTls=false; keep existing no-auth block in `{{- else }}` — per contract `contracts/dapr-cloud-pubsub.yaml`
- [x] T-705b [P] [US1] Add conditional guard to `helm/todo-chatbot/templates/kafka/redpanda-deployment.yaml` — wrap entire content with `{{- if and .Values.kafka.enabled (not .Values.kafka.external) }}` so local Redpanda only deploys when not using external cloud Kafka
- [x] T-705c [P] [US1] Add conditional guard to `helm/todo-chatbot/templates/kafka/redpanda-service.yaml` — wrap entire content with `{{- if and .Values.kafka.enabled (not .Values.kafka.external) }}` (same logic as T-705b)
- [x] T-705d [US1] Create `helm/todo-chatbot/values-cloud.yaml` per contract `contracts/helm-cloud-values.yaml` — ghcr.io images, pullPolicy=Always, frontend LoadBalancer, backend ClusterIP, dapr enabled, kafka.external=true, resource limits for ARM64, secrets placeholders
- [x] T-705e [US1] Update `helm/todo-chatbot/Chart.yaml` — version: `3.0.0`, appVersion: `5.0.0-partc`, add keywords: cloud, oke, cicd
- [x] T-705f [US1] Validate Helm chart — `helm lint ./helm/todo-chatbot -f ./helm/todo-chatbot/values.yaml -f ./helm/todo-chatbot/values-cloud.yaml` passes with 0 errors
- [x] T-705g [US1] Validate Helm template rendering — `helm template todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values.yaml -f ./helm/todo-chatbot/values-cloud.yaml` renders correctly (no template errors, pubsub has SASL block, no local Redpanda resources)

**Gate**: `helm lint` passes; `helm template` renders correctly for cloud values.

### T-706: Multi-Architecture Docker Images [US1]

- [ ] T-706a [US1] Create Docker buildx multi-arch builder — `docker buildx create --name multiarch --use`
- [ ] T-706b [US1] Login to GitHub Container Registry — `docker login ghcr.io -u <username> -p <token>`
- [ ] T-706c [US1] Build and push backend image (ARM64+AMD64) — `docker buildx build --platform linux/amd64,linux/arm64 -f docker/Dockerfile.backend -t ghcr.io/<owner>/todo-backend:latest --push .`
- [ ] T-706d [US1] Build and push frontend image (ARM64+AMD64) — `docker buildx build --platform linux/amd64,linux/arm64 -f docker/Dockerfile.frontend -t ghcr.io/<owner>/todo-frontend:latest --push .`
- [ ] T-706e [US1] Verify images exist in ghcr.io — check `ghcr.io/<owner>/todo-backend` and `ghcr.io/<owner>/todo-frontend` are accessible with multi-arch manifests

**Gate**: ARM64+AMD64 images available in ghcr.io.

### T-707: Deploy Application to OKE [US1]

- [ ] T-707a [US1] Create Kubernetes secret `todo-secrets` — `kubectl create secret generic todo-secrets --from-literal=database-url=<NEON_URL> --from-literal=cohere-api-key=<COHERE_KEY> --from-literal=jwt-secret=<JWT_SECRET>`
- [ ] T-707b [US1] Deploy with Helm — `helm upgrade --install todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values.yaml -f ./helm/todo-chatbot/values-cloud.yaml --set kafka.brokerUrl="<REDPANDA_URL>:9092" --set secrets.databaseUrl="<NEON_URL>" --set secrets.cohereApiKey="<COHERE_KEY>" --set secrets.jwtSecret="<JWT_SECRET>"`
- [ ] T-707c [US1] Verify pods running — `kubectl get pods` shows frontend and backend with 2/2 containers (app + Dapr sidecar), Running status, 0 restarts
- [ ] T-707d [US1] Wait for LoadBalancer IP — `kubectl get svc -w` until EXTERNAL-IP is assigned for frontend service
- [ ] T-707e [US1] Test frontend access — open `http://<EXTERNAL-IP>:3000` in browser, verify login page loads
- [ ] T-707f [US1] Test full flow — login → dashboard → create task via chatbot → verify response — all Phase V Part A features working identically on cloud (SC-007)

**Checkpoint US1**: Application publicly accessible via LoadBalancer IP. All core features working. SC-001, SC-002, SC-007 verified.

---

## Phase 3: User Story 2 — Cloud Kafka Integration via Redpanda Cloud (Priority: P2)

**Goal**: Configure Redpanda Cloud Kafka, verify task lifecycle events flow through Dapr Pub/Sub.

**Independent Test**: Create task via chatbot → open Redpanda Cloud console → verify `task-events` topic has CloudEvents-formatted message.

### T-704: Redpanda Cloud Kafka Setup [US2]

- [ ] T-704a [US2] Create Redpanda Cloud serverless cluster (free tier) — note bootstrap URL
- [ ] T-704b [US2] Create SASL user (SCRAM-SHA-256) — note username and password
- [ ] T-704c [US2] Create Kafka topics in Redpanda Console: `task-events` (1 partition), `reminders` (1 partition), `task-updates` (1 partition)
- [ ] T-704d [US2] Verify 3 topics visible in Redpanda Cloud console (SC-009)
- [ ] T-704e [US2] Create Kubernetes secret `kafka-secrets` — `kubectl create secret generic kafka-secrets --from-literal=username=<REDPANDA_USER> --from-literal=password=<REDPANDA_PASSWORD>`
- [ ] T-704f [US2] Verify secret — `kubectl get secret kafka-secrets`

### T-708: Event Flow Verification [US2]

- [ ] T-708a [US2] Check Dapr sidecar logs for component initialization — `kubectl logs <backend-pod> -c daprd` shows kafka-pubsub, statestore, secretstore, jobs components initialized (SC-008)
- [ ] T-708b [US2] Create task via chatbot on public URL — verify `task.created` event appears in Redpanda Cloud console `task-events` topic within 5 seconds (SC-003)
- [ ] T-708c [US2] Complete task via chatbot — verify `task.completed` event appears in `task-events` topic
- [ ] T-708d [US2] Verify CloudEvents 1.0 schema in messages — check event has `specversion`, `type`, `source`, `id`, `data` fields (FR-012)
- [ ] T-708e [US2] Verify all 5 Dapr building blocks operational:
  - Pub/Sub: event in Redpanda topic (FR-003)
  - State Store: backend sidecar logs show state operations (FR-003)
  - Secrets: backend starts without auth errors (FR-005)
  - Jobs: schedule reminder via API, callback received (FR-013)
  - Service Invocation: frontend→backend call succeeds (FR-003)

**Checkpoint US2**: Events flowing to Redpanda Cloud. All 5 Dapr blocks verified. SC-003, SC-008, SC-009 verified.

---

## Phase 4: User Story 3 — CI/CD Pipeline via GitHub Actions (Priority: P3)

**Goal**: Automated build/push/deploy pipeline triggered on push to main/deploy branch.

**Independent Test**: Push minor code change → GitHub Actions runs → change live on public URL within 15 minutes.

### T-709: CI/CD Pipeline Creation [US3]

- [x] T-709a [US3] Create `.github/workflows/deploy-cloud.yml` per contract `contracts/github-actions-schema.yml` — workflow triggers on push to main/deploy branches (paths: phase5/**), builds multi-arch images, pushes to ghcr.io, configures OCI CLI, sets up kubectl for OKE, runs helm upgrade
- [ ] T-709b [US3] Configure 12 GitHub repository secrets:
  - `OCI_CLI_USER` — OCI User OCID
  - `OCI_CLI_TENANCY` — OCI Tenancy OCID
  - `OCI_CLI_FINGERPRINT` — OCI API Key fingerprint
  - `OCI_CLI_KEY_CONTENT` — OCI API private key (base64 encoded)
  - `OCI_CLI_REGION` — e.g., us-ashburn-1
  - `OKE_CLUSTER_OCID` — OKE Cluster OCID
  - `DATABASE_URL` — Neon PostgreSQL connection string
  - `COHERE_API_KEY` — Cohere API key
  - `JWT_SECRET` — JWT signing secret
  - `KAFKA_BROKER_URL` — Redpanda Cloud bootstrap URL
  - `KAFKA_USERNAME` — Redpanda SASL username
  - `KAFKA_PASSWORD` — Redpanda SASL password
- [x] T-709c [US3] Validate workflow YAML — run `actionlint .github/workflows/deploy-cloud.yml` or manual YAML syntax check (SC-010)

### T-710: CI/CD Pipeline Verification [US3]

- [ ] T-710a [US3] Push test change to deploy branch — trigger GitHub Actions workflow
- [ ] T-710b [US3] Verify workflow triggers in GitHub Actions UI — job starts automatically
- [ ] T-710c [US3] Verify build+push steps succeed — images pushed to ghcr.io with commit SHA tag
- [ ] T-710d [US3] Verify helm deploy step succeeds — `kubectl rollout status` shows updated pods
- [ ] T-710e [US3] Verify change is live on public URL — browse to LoadBalancer IP, confirm update visible
- [ ] T-710f [US3] Confirm pipeline completes within 15 minutes (SC-004)

**Checkpoint US3**: CI/CD pipeline runs end-to-end. SC-004, SC-010 verified.

---

## Phase 5: User Story 4 — Monitoring, Logging & Documentation (Priority: P4)

**Goal**: Verify logging/monitoring access, create comprehensive deployment documentation.

**Independent Test**: `kubectl logs` shows structured output for all pods; documentation enables new developer to reproduce setup in <60 minutes.

### T-711: Monitoring & Logging Verification [US4]

- [ ] T-711a [US4] Verify application logs — `kubectl logs <backend-pod> -c todo-backend` shows structured FastAPI logs (FR-014)
- [ ] T-711b [US4] Verify Dapr sidecar logs — `kubectl logs <backend-pod> -c daprd` shows component init and event publish activity (FR-014)
- [ ] T-711c [US4] Verify frontend logs — `kubectl logs <frontend-pod> -c todo-frontend` shows Next.js production logs
- [ ] T-711d [US4] Access OCI Monitoring dashboard — verify node CPU, memory, and pod health metrics visible

### T-712: Documentation & Final Validation [US4]

- [x] T-712a [US4] Create `docs/CLOUD-DEPLOYMENT.md` with sections: Prerequisites, Oracle Cloud signup, OKE cluster creation, Redpanda Cloud setup, Docker multi-arch builds, Helm cloud deployment, CI/CD setup, Monitoring & logging, Troubleshooting guide, Cost report ($0 confirmed), Public demo URL (FR-015, SC-006)
- [x] T-712b [P] [US4] Update `README.md` with Phase V Part C section — public URL, deployment instructions link, $0 cost badge
- [x] T-712c [US4] Create deploy helper scripts:
  - `scripts/deploy-cloud.sh` — Linux/Mac cloud deploy script
  - `scripts/deploy-cloud.ps1` — Windows cloud deploy script
- [ ] T-712d [US4] Verify OCI billing shows $0.00 charges — screenshot or confirm in OCI Console (SC-005)
- [ ] T-712e [US4] Run full E2E validation checklist:
  - Frontend accessible via LoadBalancer IP (SC-001)
  - All pods 2/2 Running, 0 restarts for 10+ minutes (SC-002)
  - Events in Redpanda Cloud within 5s of task creation (SC-003)
  - CI/CD completes within 15 minutes (SC-004)
  - $0 cost confirmed (SC-005)
  - All Part A features working on cloud (SC-007)
  - Dapr sidecar logs show 5 blocks initialized (SC-008)
  - 3 Kafka topics accessible (SC-009)
- [ ] T-712f [US4] Run quickstart.md validation — follow `specs/007-phase5-partc-cloud-deployment/quickstart.md` steps to confirm accuracy

**Checkpoint US4**: Documentation complete. All 10 success criteria verified. SC-005, SC-006 confirmed.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Research (T-701)
    └── No dependencies — start immediately

Phase 2: US1 — Cluster, Helm, Docker, Deploy (T-702 → T-703 → T-705 → T-706 → T-707)
    └── Depends on Phase 1 (T-701) completion
    └── T-704 (Redpanda setup) can run in parallel with T-702/T-703

Phase 3: US2 — Kafka Events (T-704 → T-708)
    └── T-704 can start after T-701b
    └── T-708 requires T-707 (app deployed) + T-704 (Kafka ready)

Phase 4: US3 — CI/CD (T-709 → T-710)
    └── Depends on Phase 2 (working deployment) + Phase 3 (Kafka configured)

Phase 5: US4 — Monitoring & Docs (T-711 → T-712)
    └── Depends on Phases 2, 3, 4 all complete
```

### Critical Path

```
T-701 → T-702 → T-703 → T-705 → T-706 → T-707 → T-708 → T-709 → T-710 → T-711 → T-712
  │                                                   ▲
  └── T-704 (Redpanda) ──────────────────────────────┘
       (parallel with T-702/T-703/T-705)
```

### Parallel Opportunities

- T-701a through T-701e: All prerequisite checks run in parallel
- T-704 (Redpanda Cloud setup): Can run in parallel with T-702, T-703, T-705
- T-705b and T-705c: Conditional guards on different files, parallel OK
- T-706c and T-706d: Backend and frontend image builds can overlap if buildx supports it
- T-712a and T-712b: Documentation files are independent

### Within Each Task Group

1. Prerequisites verified before cluster creation
2. Cluster ready before Dapr install
3. Dapr healthy before Helm chart updates
4. Helm chart valid before Docker image push
5. Images in registry before Helm deploy
6. App deployed before event verification
7. Events verified before CI/CD pipeline
8. All systems working before documentation

---

## Success Criteria Traceability

| Success Criteria | Task(s) | Phase |
|------------------|---------|-------|
| SC-001: App accessible via LoadBalancer IP | T-707d, T-707e | 2 (US1) |
| SC-002: Pods 2/2 Running, 0 restarts 10min | T-707c | 2 (US1) |
| SC-003: Events in Redpanda within 5s | T-708b | 3 (US2) |
| SC-004: CI/CD completes within 15min | T-710f | 4 (US3) |
| SC-005: $0 OCI billing | T-712d | 5 (US4) |
| SC-006: New dev setup < 60min with docs | T-712a | 5 (US4) |
| SC-007: All Part A features on cloud | T-707f | 2 (US1) |
| SC-008: Dapr sidecar shows 5 blocks init | T-708a | 3 (US2) |
| SC-009: 3 Kafka topics in Redpanda | T-704d | 3 (US2) |
| SC-010: Workflow YAML lint passes | T-709c | 4 (US3) |

---

## Functional Requirements Traceability

| Requirement | Task(s) | Description |
|-------------|---------|-------------|
| FR-001 | T-702a | OKE Always Free (A1.Flex, 4 OCPU, 24GB) |
| FR-002 | T-703a, T-703b | Dapr installed, all components healthy |
| FR-003 | T-708e | All 5 Dapr building blocks verified |
| FR-004 | T-704a, T-704b, T-705a | Redpanda Cloud SASL/SCRAM auth |
| FR-005 | T-707a, T-704e | K8s secrets for credentials |
| FR-006 | T-705d, T-707b | Helm deploy with values-cloud.yaml |
| FR-007 | T-707d, T-707e | Frontend LoadBalancer public access |
| FR-008 | T-705d | Backend ClusterIP (not public) |
| FR-009 | T-709a | GitHub Actions CI/CD workflow |
| FR-010 | T-706c, T-706d | Images pushed to ghcr.io |
| FR-011 | T-707f | Backward compatibility verified |
| FR-012 | T-708d | CloudEvents 1.0 events in Kafka |
| FR-013 | T-708e | Dapr Jobs API for reminders |
| FR-014 | T-711a, T-711b | Pod and Dapr sidecar logs accessible |
| FR-015 | T-712a | Comprehensive deployment documentation |

---

## Implementation Strategy

### Execution Rules

1. **One task at a time**: Complete and verify each task before moving to the next
2. **Step-by-step with confirmation**: Each task requires explicit verification before proceeding
3. **Interactive**: Pause at gates and checkpoints for user confirmation
4. **No shortcuts**: Follow the exact order — T-701 → T-712
5. **Rollback on failure**: If a task fails, diagnose and fix before proceeding

### MVP First (US1 Only)

1. Complete Phase 1: Research (T-701)
2. Complete US1: Cluster + Deploy (T-702 → T-707)
3. **STOP and VALIDATE**: Test full application flow on public URL
4. This is the MVP — publicly accessible Todo Chatbot on cloud

### Incremental Delivery

1. T-701 → Prerequisites confirmed
2. T-702 → T-707 → MVP deployed (US1 complete)
3. T-704 + T-708 → Events flowing (US2 complete)
4. T-709 + T-710 → CI/CD automated (US3 complete)
5. T-711 + T-712 → Documented and verified (US4 complete)

---

## Notes

- All tasks are infrastructure/configuration only — NO application code changes
- [P] tasks = different files, no dependencies between them
- Docker base images (python:3.12-slim, node:20-alpine) already support ARM64 natively
- The `kafka.external` flag is the key conditional for cloud vs. local Dapr pubsub
- Helm values overlay: `values.yaml` (base) → `values-cloud.yaml` (cloud override)
- Total files to create/modify: ~8 (values-cloud.yaml, pubsub template, 2 Redpanda guards, Chart.yaml, CI/CD workflow, deploy scripts, docs)
- All 15 FRs and 10 SCs have task traceability above
