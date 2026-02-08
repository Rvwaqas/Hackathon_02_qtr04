# Implementation Plan: Phase V Part C - Cloud Deployment on Oracle OKE

**Branch**: `007-phase5-partc-cloud-deployment` | **Date**: 2026-02-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/007-phase5-partc-cloud-deployment/spec.md`

---

## Summary

Deploy the existing AI-Powered Todo Chatbot (Phase V Part A code + Part B Dapr patterns) to Oracle Cloud Always Free OKE cluster with Redpanda Cloud Kafka, GitHub Actions CI/CD, public LoadBalancer access, and basic monitoring. No application code changes — only infrastructure configuration, Helm cloud overrides, CI/CD pipeline, and documentation.

---

## Technical Context

**Language/Version**: Python 3.12 (backend), Node.js 20 (frontend) — unchanged from Part A/B
**Primary Dependencies**: FastAPI, Next.js 15, Dapr 1.12+, Helm 3.x — unchanged
**Storage**: Neon PostgreSQL (external, unchanged), Dapr state.postgresql (cache)
**Testing**: Infrastructure validation only (kubectl, dapr, helm commands) — no new unit tests
**Target Platform**: Oracle Cloud OKE (ARM64 / Ampere A1.Flex Always Free)
**Project Type**: Web (backend/frontend) — unchanged
**Performance Goals**: Application accessible within 15 min of Helm deploy; events in Kafka within 5s
**Constraints**: $0 cost (Oracle Always Free + Redpanda Cloud free tier); ARM64 images required
**Scale/Scope**: 2 pods (frontend + backend) with Dapr sidecars; 3 Kafka topics; 1 CI/CD pipeline

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Plan Alignment | Status |
|-----------|----------------|--------|
| P1: Spec-Driven Development | All tasks reference spec FR/SC/US | COMPLIANT |
| P2: AI-Assisted Infrastructure | kubectl-ai, kagent, HelmAgent, CloudDeployAgent | COMPLIANT |
| P3: Backward Compatibility | No application code changes; Part A/B fully preserved | COMPLIANT |
| P4: Full Dapr Runtime on Cloud | All 5 building blocks configured for OKE | COMPLIANT |
| P5: Dapr-Exclusive Distributed | Same Dapr patterns from Part B; no direct Kafka client | COMPLIANT |
| P6: Cloud Kafka via Managed Service | Redpanda Cloud serverless (free tier) chosen | COMPLIANT |
| P7: Extend Part B Helm Charts | values-cloud.yaml overlay on existing chart | COMPLIANT |
| P8: Cost Control | Oracle Always Free + Redpanda Cloud free tier = $0 | COMPLIANT |
| P9: CI/CD Pipeline Required | GitHub Actions workflow for build/push/deploy | COMPLIANT |

### Non-Negotiable Gates

| Non-Negotiable | Enforcement | Status |
|----------------|-------------|--------|
| No hardcoded secrets | K8s secrets + Dapr secretstore | GATE PASS |
| No exposed env vars | Secrets via secretKeyRef only | GATE PASS |
| No Phase III/IV/A/B breakage | No app code changes | GATE PASS |
| No paid resources | Oracle AF + Redpanda free | GATE PASS |
| No public backend | ClusterIP service type | GATE PASS |
| CI/CD for deployments | GitHub Actions workflow | GATE PASS |
| No credentials in git | GitHub encrypted secrets | GATE PASS |

---

## Project Structure

### Documentation (this feature)

```text
specs/007-phase5-partc-cloud-deployment/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0: OKE/Redpanda/OCIR research
├── data-model.md        # N/A (no new data models)
├── quickstart.md        # Cloud deployment quickstart guide
├── contracts/           # Cloud-specific contracts
│   ├── dapr-cloud-pubsub.yaml    # Redpanda Cloud Dapr component
│   ├── github-actions-schema.yml # CI/CD workflow contract
│   └── helm-cloud-values.yaml    # values-cloud.yaml contract
├── checklists/
│   └── requirements.md  # Spec quality checklist
└── tasks.md             # Task breakdown (/sp.tasks output)
```

### Source Code (new/modified files)

```text
phase5/
├── helm/todo-chatbot/
│   ├── Chart.yaml                    # UPDATED: version 3.0.0-partc
│   ├── values.yaml                   # UNCHANGED (base)
│   ├── values-dapr.yaml              # UNCHANGED (Part B local)
│   ├── values-local.yaml             # UNCHANGED (Minikube)
│   ├── values-cloud.yaml             # NEW: OKE cloud overrides
│   └── templates/
│       ├── dapr/
│       │   ├── pubsub-kafka.yaml     # UPDATED: conditional SASL auth
│       │   ├── statestore.yaml       # UNCHANGED
│       │   └── secretstore.yaml      # UNCHANGED
│       ├── kafka/
│       │   ├── redpanda-deployment.yaml  # UNCHANGED (local only)
│       │   └── redpanda-service.yaml     # UNCHANGED (local only)
│       └── (all other templates unchanged)
│
├── docker/
│   ├── Dockerfile.backend            # UPDATED: multi-platform support
│   └── Dockerfile.frontend           # UPDATED: multi-platform support
│
├── .github/workflows/
│   └── deploy-cloud.yml              # NEW: CI/CD pipeline
│
├── scripts/
│   ├── deploy-cloud.ps1              # NEW: Windows cloud deploy script
│   └── deploy-cloud.sh               # NEW: Linux/Mac cloud deploy script
│
└── docs/
    └── CLOUD-DEPLOYMENT.md           # NEW: Full cloud deployment guide
```

**Structure Decision**: Extend existing Phase V Part B structure. No new application code directories. Changes limited to Helm values, Dapr component templates, Docker build config, CI/CD workflow, and documentation.

---

## Key Decisions & Tradeoffs

| Decision | Chosen Option | Alternatives Considered | Rationale |
|----------|---------------|------------------------|-----------|
| Cloud Provider | Oracle OKE Always Free | DOKS ($200/60d), AKS ($200/30d), GKE ($300/90d) | Permanent free tier; ARM64 Ampere A1 with 4 OCPU + 24GB; no credit expiration |
| Kafka Provider | Redpanda Cloud serverless | Confluent Cloud, self-hosted Strimzi | Zero ops; free tier (1GB); SASL/SCRAM auth; Kafka-compatible |
| Container Registry | GitHub Container Registry (ghcr.io) | Oracle OCIR, Docker Hub | Free for public repos; no OCI auth complexity; GitHub Actions native integration |
| CI/CD | GitHub Actions | GitLab CI, Jenkins, ArgoCD | Free for public repos; simple YAML; native GitHub integration; no separate infra |
| Frontend Access | OCI LoadBalancer | Ingress + nginx, NodePort | Free on OCI; simplest public access; auto-assigns external IP |
| Docker Platform | Multi-arch buildx (ARM64 + AMD64) | ARM64-only | OKE Always Free uses Ampere A1 (ARM64); local dev uses AMD64; buildx handles both |
| Secrets Management | K8s Secrets + Dapr secretstore | OCI Vault, Sealed Secrets | Simplest; free; Dapr-compatible; same pattern as Part B |
| Helm Strategy | values-cloud.yaml overlay | Separate cloud chart, Kustomize | Reuses Part B chart; single chart multi-env; Helm best practice |

---

## Phase 0: Research & Prerequisites

### 0.1 Oracle Cloud Infrastructure (OCI)

| Topic | Research Needed |
|-------|-----------------|
| OKE Always Free shapes | VM.Standard.A1.Flex: 4 OCPUs, 24GB, ARM64 Ampere |
| Node pool configuration | 1 node pool, 2 nodes (2 OCPU + 12GB each) |
| OCI CLI setup | `oci ce cluster create-kubeconfig` for kubectl access |
| OCI LoadBalancer | Free tier includes 1 LoadBalancer (10 Mbps) |
| OCIR vs ghcr.io | ghcr.io preferred (simpler auth in GitHub Actions) |

### 0.2 Redpanda Cloud

| Topic | Research Needed |
|-------|-----------------|
| Serverless free tier | 1 GB storage, limited throughput, SASL/SCRAM |
| Bootstrap URL format | `<cluster-id>.any.us-east-1.mpx.prd.cloud.redpanda.com:9092` |
| SASL mechanism | SCRAM-SHA-256 with username/password |
| Topic management | Create via Redpanda Console UI |
| TLS requirement | TLS enabled by default on cloud |

### 0.3 ARM64 Docker Images

| Topic | Research Needed |
|-------|-----------------|
| Python 3.12 ARM64 | `python:3.12-slim` supports linux/arm64 natively |
| Node 20 ARM64 | `node:20-alpine` supports linux/arm64 natively |
| Docker buildx setup | `docker buildx create --use` + `--platform linux/amd64,linux/arm64` |
| GitHub Actions buildx | `docker/setup-buildx-action` + `docker/build-push-action` |

---

## Phase 1: Cloud Account & Cluster Setup (US1 — P1 MVP)

### 1.1 Oracle Cloud Account

| Step | Action | Agent |
|------|--------|-------|
| 1.1.1 | Sign up at oracle.com/cloud/free | User (manual) |
| 1.1.2 | Verify email and set up tenancy | User (manual) |
| 1.1.3 | Install OCI CLI locally | CloudDeployAgent |
| 1.1.4 | Configure OCI CLI (`oci setup config`) | CloudDeployAgent |

### 1.2 OKE Cluster Creation

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 1.2.1 | Create VCN with public/private subnets | CloudDeployAgent | FR-001 |
| 1.2.2 | Create OKE cluster (Kubernetes 1.28+) | CloudDeployAgent | FR-001 |
| 1.2.3 | Create node pool: 2 nodes, A1.Flex (2 OCPU + 12GB each) | CloudDeployAgent | FR-001 |
| 1.2.4 | Download kubeconfig: `oci ce cluster create-kubeconfig` | CloudDeployAgent | SC-002 |
| 1.2.5 | Verify: `kubectl get nodes` shows 2 Ready nodes | CloudDeployAgent | SC-002 |

**OKE Node Pool Configuration**:
```
Shape: VM.Standard.A1.Flex
OCPUs per node: 2
Memory per node: 12 GB
Node count: 2
Total: 4 OCPUs, 24 GB (within Always Free)
```

### 1.3 Dapr Installation on OKE

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 1.3.1 | Install Dapr CLI (if not present) | K8sAgent | FR-002 |
| 1.3.2 | Run `dapr init -k --wait` on OKE | K8sAgent | FR-002 |
| 1.3.3 | Verify: `dapr status -k` all healthy | K8sAgent | SC-008 |
| 1.3.4 | Verify: `kubectl get pods -n dapr-system` all Running | K8sAgent | SC-008 |

**Gate**: kubectl connected + Dapr healthy on OKE

---

## Phase 2: Redpanda Cloud Kafka Setup (US2 — P2)

### 2.1 Redpanda Cloud Account & Cluster

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 2.1.1 | Sign up at redpanda.com/cloud (free) | User (manual) |
| 2.1.2 | Create serverless cluster in closest region | User (manual) |
| 2.1.3 | Note bootstrap URL | KafkaAgent | FR-004 |
| 2.1.4 | Create SASL user (SCRAM-SHA-256) | User (manual) |
| 2.1.5 | Note username and password | KafkaAgent | FR-004 |

### 2.2 Topics Creation

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 2.2.1 | Create topic: `task-events` (1 partition) | KafkaAgent | SC-009 |
| 2.2.2 | Create topic: `reminders` (1 partition) | KafkaAgent | SC-009 |
| 2.2.3 | Create topic: `task-updates` (1 partition) | KafkaAgent | SC-009 |
| 2.2.4 | Verify topics in Redpanda Console | KafkaAgent | SC-009 |

### 2.3 Kubernetes Secrets for Kafka

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 2.3.1 | Create K8s secret `kafka-secrets` with username + password | K8sAgent | FR-005 |
| 2.3.2 | Verify secret exists: `kubectl get secret kafka-secrets` | K8sAgent | FR-005 |

**Gate**: Redpanda Cloud accessible, topics created, K8s secrets stored

---

## Phase 3: Helm Chart Cloud Extensions (US1 — P1)

### 3.1 Dapr Pubsub Template Update

The existing `templates/dapr/pubsub-kafka.yaml` currently hardcodes `authRequired: "false"` for local Redpanda. For cloud, it needs conditional SASL support.

**Change**: Update pubsub-kafka.yaml to support both local (no auth) and cloud (SASL) via values.

```yaml
# Current (Part B): authRequired: "false"
# New (Part C): Conditional based on kafka.external flag
{{- if .Values.kafka.external }}
    - name: authRequired
      value: "true"
    - name: saslUsername
      secretKeyRef:
        name: kafka-secrets
        key: username
    - name: saslPassword
      secretKeyRef:
        name: kafka-secrets
        key: password
    - name: saslMechanism
      value: "SCRAM-SHA-256"
    - name: authType
      value: "password"
auth:
  secretStore: kubernetes-secrets
{{- else }}
    - name: authRequired
      value: "false"
{{- end }}
```

### 3.2 Create values-cloud.yaml

| Setting | Value | Rationale |
|---------|-------|-----------|
| `backend.replicas` | 1 | Resource constraints (Always Free) |
| `backend.image.repository` | `ghcr.io/<owner>/todo-backend` | GitHub Container Registry |
| `backend.image.pullPolicy` | `Always` | Cloud registry (not local) |
| `frontend.replicas` | 1 | Resource constraints |
| `frontend.image.repository` | `ghcr.io/<owner>/todo-frontend` | GitHub Container Registry |
| `frontend.image.pullPolicy` | `Always` | Cloud registry |
| `frontend.service.type` | `LoadBalancer` | Public access (FR-007) |
| `frontend.service.nodePort` | removed | Not needed for LoadBalancer |
| `dapr.enabled` | `true` | Full Dapr on cloud |
| `dapr.logLevel` | `warn` | Reduce sidecar resource usage |
| `kafka.enabled` | `true` | Enable Kafka integration |
| `kafka.external` | `true` | Use Redpanda Cloud (not local) |
| `kafka.brokerUrl` | `<redpanda-cloud-url>:9092` | Placeholder for actual URL |
| `redpanda.enabled` | `false` | No local Redpanda on cloud |
| Backend resources | 200m CPU / 384Mi mem (requests) | ARM64 optimized |
| Frontend resources | 150m CPU / 256Mi mem (requests) | ARM64 optimized |

### 3.3 Update Chart.yaml

- Version: `3.0.0` (Part C)
- appVersion: `5.0.0-partc`
- Add keyword: `cloud`, `oke`, `cicd`

### 3.4 Conditional Redpanda Deployment

Existing `templates/kafka/redpanda-deployment.yaml` and `redpanda-service.yaml` MUST be wrapped with:
```yaml
{{- if and .Values.kafka.enabled (not .Values.kafka.external) }}
```
So they only deploy for local (Part B) and are skipped for cloud (Part C).

**Gate**: `helm lint` passes with values-cloud.yaml; `helm template` renders correctly

---

## Phase 4: Multi-Architecture Docker Images (US1 — P1)

### 4.1 Docker Buildx Setup

OKE Always Free uses ARM64 (Ampere A1). Current Dockerfiles use `python:3.12-slim` and `node:20-alpine` which both support ARM64 natively. No Dockerfile changes needed — only the build command changes.

**Build commands**:
```bash
# Setup buildx (one-time)
docker buildx create --name multiarch --use

# Build and push backend (ARM64 + AMD64)
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.backend \
  -t ghcr.io/<owner>/todo-backend:latest \
  --push .

# Build and push frontend (ARM64 + AMD64)
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.frontend \
  -t ghcr.io/<owner>/todo-frontend:latest \
  --push .
```

### 4.2 GitHub Container Registry Setup

| Step | Action | Agent |
|------|--------|-------|
| 4.2.1 | Create GitHub PAT with `write:packages` scope | User (manual) |
| 4.2.2 | Login: `docker login ghcr.io -u <user> -p <token>` | CloudDeployAgent |
| 4.2.3 | Build + push multi-arch images | DockerAgent |
| 4.2.4 | Verify images at `ghcr.io/<owner>/todo-backend` | CloudDeployAgent |

**Gate**: ARM64 images available in ghcr.io

---

## Phase 5: Application Deployment on OKE (US1 — P1)

### 5.1 Kubernetes Secrets

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 5.1.1 | Create secret `todo-secrets` (DATABASE_URL, COHERE_API_KEY, JWT_SECRET) | K8sAgent | FR-005 |
| 5.1.2 | Create secret `kafka-secrets` (username, password) — if not done in Phase 2 | K8sAgent | FR-005 |
| 5.1.3 | Create `ghcr-pull-secret` for image pulling (if repo is private) | K8sAgent | FR-010 |

### 5.2 Helm Deployment

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 5.2.1 | Run `helm upgrade --install` with cloud values | HelmAgent | FR-006, SC-001 |
| 5.2.2 | Verify pods Running 2/2: `kubectl get pods` | K8sAgent | SC-002 |
| 5.2.3 | Wait for LoadBalancer IP: `kubectl get svc -w` | K8sAgent | SC-001 |
| 5.2.4 | Test frontend access via external IP | K8sAgent | FR-007, SC-001 |
| 5.2.5 | Test login and chatbot flow | OrchestratorAgent | SC-007 |

**Helm install command**:
```bash
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values.yaml \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  --set secrets.databaseUrl="<NEON_URL>" \
  --set secrets.cohereApiKey="<COHERE_KEY>" \
  --set secrets.jwtSecret="<JWT_SECRET>" \
  --set kafka.brokerUrl="<REDPANDA_CLOUD_URL>:9092"
```

**Gate**: App publicly accessible, all features working

---

## Phase 6: Event Flow Verification (US2 — P2)

### 6.1 Pub/Sub Verification

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 6.1.1 | Check Dapr sidecar logs for component init | K8sAgent | SC-008 |
| 6.1.2 | Create task via chatbot on public URL | OrchestratorAgent | SC-003 |
| 6.1.3 | Check Redpanda Cloud console for event in task-events | KafkaAgent | SC-003 |
| 6.1.4 | Complete task, verify task.completed event | OrchestratorAgent | FR-012 |
| 6.1.5 | Verify CloudEvents 1.0 schema in messages | KafkaAgent | FR-012 |

### 6.2 Dapr Building Blocks Verification

| Building Block | Test Method | Expected | Spec Reference |
|----------------|-------------|----------|----------------|
| Pub/Sub | Create task → check Redpanda console | Event in topic | FR-003, SC-003 |
| State Store | Backend sidecar logs | State operations logged | FR-003 |
| Secrets | Backend starts with API key | No auth errors | FR-003, FR-005 |
| Jobs | Schedule reminder via API | Callback received | FR-003, FR-013 |
| Service Invocation | Frontend→Backend call | Response received | FR-003 |

**Gate**: Events flowing to Redpanda Cloud; all 5 Dapr blocks operational

---

## Phase 7: CI/CD Pipeline (US3 — P3)

### 7.1 GitHub Actions Workflow

Create `.github/workflows/deploy-cloud.yml`:

**Workflow structure**:
```
Trigger: push to main or deploy branch (paths: phase5/**)
Jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      1. Checkout code
      2. Set up Docker Buildx
      3. Login to ghcr.io
      4. Build + push backend (multi-arch)
      5. Build + push frontend (multi-arch)
      6. Set up kubectl + OCI CLI
      7. Configure kubeconfig for OKE
      8. Run helm upgrade --install with cloud values
      9. Verify deployment health
```

### 7.2 GitHub Repository Secrets

| Secret Name | Value Source | Spec Reference |
|-------------|-------------|----------------|
| `OCI_CLI_USER` | OCI Console → User OCID | FR-009 |
| `OCI_CLI_TENANCY` | OCI Console → Tenancy OCID | FR-009 |
| `OCI_CLI_FINGERPRINT` | OCI API Key fingerprint | FR-009 |
| `OCI_CLI_KEY_CONTENT` | OCI API private key (base64) | FR-009 |
| `OCI_CLI_REGION` | e.g., `us-ashburn-1` | FR-009 |
| `OKE_CLUSTER_OCID` | OCI Console → Cluster OCID | FR-009 |
| `DATABASE_URL` | Neon connection string | FR-005 |
| `COHERE_API_KEY` | Cohere dashboard | FR-005 |
| `JWT_SECRET` | Generated secret | FR-005 |
| `KAFKA_BROKER_URL` | Redpanda Cloud bootstrap | FR-004 |
| `KAFKA_USERNAME` | Redpanda Cloud SASL user | FR-004 |
| `KAFKA_PASSWORD` | Redpanda Cloud SASL password | FR-004 |

### 7.3 Pipeline Verification

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 7.3.1 | Push a test change to deploy branch | CloudDeployAgent | SC-004 |
| 7.3.2 | Verify workflow triggers in GitHub UI | CloudDeployAgent | SC-004 |
| 7.3.3 | Verify build + push steps succeed | CloudDeployAgent | SC-004 |
| 7.3.4 | Verify helm deploy step succeeds | CloudDeployAgent | SC-004 |
| 7.3.5 | Verify change is live on public URL | OrchestratorAgent | SC-004 |

**Gate**: CI/CD pipeline runs end-to-end successfully

---

## Phase 8: Monitoring, Logging & Documentation (US4 — P4)

### 8.1 Monitoring & Logging Setup

| Step | Action | Agent | Spec Reference |
|------|--------|-------|----------------|
| 8.1.1 | Verify `kubectl logs <pod> -c todo-backend` works | K8sAgent | FR-014 |
| 8.1.2 | Verify `kubectl logs <pod> -c daprd` shows events | K8sAgent | FR-014 |
| 8.1.3 | Access OCI Monitoring for node metrics | CloudDeployAgent | SC-008 |
| 8.1.4 | Document log access commands | OrchestratorAgent | FR-015 |

### 8.2 Documentation

| Document | Location | Contents | Spec Reference |
|----------|----------|----------|----------------|
| Cloud Deployment Guide | `docs/CLOUD-DEPLOYMENT.md` | Full setup from Oracle signup to running app | FR-015, SC-006 |
| README update | `README.md` | Part C section with public URL and demo info | FR-015 |
| Cost Report | In CLOUD-DEPLOYMENT.md | $0 confirmation with OCI billing screenshot description | SC-005 |

**Documentation sections for CLOUD-DEPLOYMENT.md**:
1. Prerequisites (accounts, CLI tools)
2. Oracle Cloud signup & OKE cluster creation
3. Redpanda Cloud setup & topics
4. Docker multi-arch image build
5. Helm deployment with cloud values
6. CI/CD pipeline setup (GitHub Actions)
7. Monitoring & logging
8. Troubleshooting guide
9. Cost report ($0 confirmed)
10. Public demo URL

**Gate**: Documentation reproducible; $0 cost confirmed

---

## Agent Responsibilities

| Agent | Responsibility | Phases |
|-------|----------------|--------|
| CloudDeployAgent | OCI account, OKE cluster, OCI CLI, CI/CD secrets | 1, 7 |
| K8sAgent | Dapr install, kubectl ops, pod verification, secrets | 1, 2, 5, 6, 8 |
| HelmAgent | Chart updates, values-cloud.yaml, helm deploy | 3, 5 |
| DaprAgent | Pubsub template update, component verification | 3, 6 |
| KafkaAgent | Redpanda Cloud setup, topic creation, event verification | 2, 6 |
| DockerAgent | Multi-arch buildx, image push | 4 |
| OrchestratorAgent | E2E testing, documentation, demo prep | 5, 6, 8 |

---

## Testing/Validation Strategy

### Infrastructure Tests

| Check | Command | Expected | Phase |
|-------|---------|----------|-------|
| OKE nodes ready | `kubectl get nodes` | 2 Ready nodes (ARM64) | 1 |
| Dapr healthy | `dapr status -k` | All components healthy | 1 |
| Kafka connected | Dapr sidecar logs | No connection errors | 6 |
| Pods running | `kubectl get pods` | 2/2 containers, 0 restarts | 5 |
| LoadBalancer IP | `kubectl get svc` | External IP assigned | 5 |

### Application Tests

| Feature | Test Method | Expected | Phase |
|---------|-------------|----------|-------|
| Frontend access | Browser → LoadBalancer IP | Login page loads | 5 |
| Login flow | Login with credentials | Dashboard displayed | 5 |
| Task CRUD | Chatbot commands | Tasks created/updated/deleted | 5 |
| Priorities | "add high priority task X" | Priority set correctly | 5 |
| Tags | "add task X #work" | Tag applied | 5 |
| Recurring | "add daily task X" | Recurrence created | 5 |
| Search | "search tasks for X" | Results filtered | 5 |
| Events | Create task → Redpanda console | CloudEvents message | 6 |

### CI/CD Tests

| Check | Method | Expected | Phase |
|-------|--------|----------|-------|
| Workflow triggers | Push to deploy branch | GitHub Actions starts | 7 |
| Build succeeds | GitHub Actions UI | Green build step | 7 |
| Push succeeds | ghcr.io packages page | New image tag | 7 |
| Deploy succeeds | kubectl rollout status | Pods updated | 7 |
| Change visible | Browser → public URL | Updated content | 7 |

---

## Success Criteria Mapping

| Spec SC | Plan Phase | Tasks | Verification |
|---------|------------|-------|--------------|
| SC-001 | Phase 5 | 5.2.3-5.2.4 | LoadBalancer IP accessible in browser |
| SC-002 | Phase 5 | 5.2.2 | `kubectl get pods` → 2/2, 0 restarts for 10min |
| SC-003 | Phase 6 | 6.1.2-6.1.3 | Event in Redpanda console within 5s |
| SC-004 | Phase 7 | 7.3.1-7.3.5 | CI/CD completes within 15min |
| SC-005 | Phase 8 | 8.2 | OCI billing = $0.00 |
| SC-006 | Phase 8 | 8.2 | Doc test: new dev setup < 60min |
| SC-007 | Phase 5 | 5.2.5 | All Part A features work on cloud |
| SC-008 | Phase 6 | 6.2 | Dapr sidecar logs show 5 blocks init |
| SC-009 | Phase 2 | 2.2.1-2.2.4 | 3 topics in Redpanda console |
| SC-010 | Phase 7 | 7.1 | `actionlint deploy-cloud.yml` → 0 errors |

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation | Phase |
|------|--------|------------|------------|-------|
| OKE Always Free insufficient for Dapr | Pods pending/OOMKilled | Medium | Reduce replicas to 1; Dapr logLevel=warn; tight resource limits | 3, 5 |
| ARM64 image build issues | Pods CrashLoopBackOff | Medium | docker buildx with --platform; verify base images support ARM64 | 4 |
| Redpanda Cloud connectivity | Events not flowing | Low | Verify OCI security lists allow outbound 9092; test curl from pod | 2, 6 |
| OCI LoadBalancer delay | App unreachable for minutes | Low | `kubectl get svc -w` with timeout; document wait procedure | 5 |
| GitHub Actions OKE auth | CI/CD fails | Medium | Use OCI CLI config in workflow; test auth step separately | 7 |
| Neon DB unreachable from OKE | App errors | Low | Neon has no IP restrictions by default; test connectivity first | 5 |

---

## Complexity Tracking

No constitution violations. All changes are additive infrastructure configuration (values-cloud.yaml, CI/CD workflow, documentation). No new application code, no new dependencies, no architectural changes.

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-02-06 | Initial implementation plan for Part C cloud deployment |
