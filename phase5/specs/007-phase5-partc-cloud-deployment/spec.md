# Feature Specification: Phase V Part C - Cloud Deployment on Oracle OKE

**Feature Branch**: `007-phase5-partc-cloud-deployment`
**Created**: 2026-02-06
**Status**: Draft
**Input**: Deploy the AI-Powered Todo Chatbot to Oracle Cloud Always Free OKE with Dapr, Redpanda Cloud Kafka, GitHub Actions CI/CD, and public access — all at zero cost.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cloud Cluster Setup & App Deployment (Priority: P1)

A developer signs up for Oracle Cloud Always Free tier, creates an OKE cluster with 4 OCPUs and 24GB RAM, configures kubectl to connect, installs Dapr on the cluster, and deploys the complete Todo Chatbot application using Helm with cloud-specific values. After deployment, the application is publicly accessible via a LoadBalancer IP address.

**Why this priority**: Without a running cloud cluster and deployed application, nothing else (CI/CD, Kafka, monitoring) can be tested or demonstrated. This is the foundational MVP.

**Independent Test**: Navigate to the LoadBalancer IP in a browser, see the login page load, login, view the dashboard with tasks, and send a chatbot command that returns a valid response.

**Acceptance Scenarios**:

1. **Given** an Oracle Cloud account on the Always Free tier, **When** the developer creates an OKE cluster via OCI Console or CLI, **Then** the cluster reports healthy with 2+ worker nodes and sufficient resources (4 OCPUs, 24GB RAM total).
2. **Given** a running OKE cluster, **When** the developer runs `dapr init -k --wait`, **Then** `dapr status -k` shows all Dapr system components healthy.
3. **Given** Dapr installed on OKE, **When** the developer runs `helm upgrade --install` with cloud values, **Then** all pods (frontend, backend) reach Running state with 2/2 containers (app + Dapr sidecar).
4. **Given** deployed pods with a LoadBalancer service, **When** the developer retrieves the external IP/URL, **Then** the frontend loads in a browser from any internet-connected device.
5. **Given** a publicly accessible frontend, **When** a user logs in and interacts with the chatbot, **Then** the full Phase V Part A feature set works identically to local deployment.

---

### User Story 2 - Cloud Kafka Integration via Redpanda Cloud (Priority: P2)

A developer creates a Redpanda Cloud serverless cluster (free tier), obtains SASL credentials and bootstrap URL, configures the Dapr pubsub.kafka component with those credentials, and verifies that task lifecycle events flow from the application through the Dapr sidecar to Redpanda Cloud Kafka topics.

**Why this priority**: Event-driven architecture is a core hackathon requirement and must be proven on cloud infrastructure. Redpanda Cloud eliminates self-hosted Kafka ops overhead.

**Independent Test**: Create a task via the chatbot, then open the Redpanda Cloud console and verify the `task-events` topic received a CloudEvents-formatted message.

**Acceptance Scenarios**:

1. **Given** a Redpanda Cloud serverless account (free tier), **When** the developer creates a cluster and obtains the bootstrap URL + SASL credentials, **Then** the cluster is reachable from the OKE pods.
2. **Given** Redpanda Cloud credentials stored as Kubernetes secrets, **When** the Dapr pubsub.kafka component is deployed referencing those secrets, **Then** Dapr sidecar logs show successful connection to the broker.
3. **Given** a connected Kafka pubsub component, **When** a user creates a task via the chatbot, **Then** a CloudEvents-formatted `task.created` event appears in the `task-events` topic within 5 seconds.
4. **Given** events flowing to Redpanda Cloud, **When** a user completes a task, **Then** a `task.completed` event appears in the `task-events` topic.
5. **Given** a configured Dapr Jobs component, **When** a reminder job is scheduled, **Then** the backend callback endpoint receives the trigger at the scheduled time.

---

### User Story 3 - CI/CD Pipeline via GitHub Actions (Priority: P3)

A developer configures a GitHub Actions workflow that automatically builds Docker images for the backend and frontend, pushes them to a container registry (OCIR or ghcr.io), and deploys to the OKE cluster via `helm upgrade` on every push to the main or deploy branch.

**Why this priority**: CI/CD automation is a hackathon bonus requirement and demonstrates production-readiness. It depends on US1 (working deployment) and US2 (Kafka config) to be meaningful.

**Independent Test**: Push a minor code change (e.g., update a health check message) to the deploy branch, observe GitHub Actions running the build/push/deploy steps, and verify the change is live on the public URL within 10 minutes.

**Acceptance Scenarios**:

1. **Given** a GitHub Actions workflow file at `.github/workflows/deploy-cloud.yml`, **When** the developer pushes to the `main` or `deploy` branch, **Then** the workflow triggers automatically.
2. **Given** a triggered workflow, **When** the build step runs, **Then** Docker images for both backend and frontend are built successfully.
3. **Given** built images, **When** the push step runs, **Then** images are pushed to the container registry with the commit SHA as tag.
4. **Given** pushed images, **When** the deploy step runs `helm upgrade --install` with the new image tag, **Then** the cloud deployment updates with the new image and pods roll out successfully.
5. **Given** a successful deployment, **When** the developer visits the public URL, **Then** the change is live (e.g., updated health check message visible).

---

### User Story 4 - Monitoring, Logging & Documentation (Priority: P4)

A developer accesses pod logs, Dapr sidecar logs, and basic cloud monitoring to verify application health. Complete documentation covers Oracle signup, cluster creation, Kafka setup, Helm configuration, CI/CD setup, and the public demo URL with a confirmed $0 cost report.

**Why this priority**: Monitoring ensures operability, and documentation enables reproducibility and hackathon evaluation. This is the final polish layer.

**Independent Test**: Run `kubectl logs` on all pods and Dapr sidecars to verify structured logs, access OCI monitoring dashboard for node metrics, and validate that the documentation is sufficient for a new developer to reproduce the entire setup.

**Acceptance Scenarios**:

1. **Given** a deployed application, **When** the developer runs `kubectl logs <backend-pod> -c todo-backend`, **Then** application logs with structured output are visible.
2. **Given** Dapr sidecars on all pods, **When** the developer runs `kubectl logs <backend-pod> -c daprd`, **Then** Dapr sidecar logs show component initialization and event publish activity.
3. **Given** an OKE cluster, **When** the developer accesses OCI Monitoring, **Then** basic node CPU, memory, and pod health metrics are visible.
4. **Given** documentation in `CLOUD-DEPLOYMENT.md`, **When** a new developer follows the steps, **Then** they can reproduce the entire setup from Oracle signup to running application.
5. **Given** all resources deployed, **When** the developer checks OCI billing, **Then** the total cost is $0 (all resources within Always Free limits).

---

### Edge Cases

- What happens when the OKE cluster node pool auto-scales beyond Always Free limits? The configuration MUST pin node count and shape to Always Free shapes only (VM.Standard.A1.Flex, max 4 OCPUs, 24GB RAM).
- What happens when Redpanda Cloud free tier storage fills up? Event publisher MUST handle publish failures gracefully (fire-and-forget pattern from Part A) and log warnings without crashing.
- What happens when the LoadBalancer external IP is not yet assigned? The deployment documentation MUST include a wait/retry procedure to poll for the IP.
- What happens when GitHub Actions secrets are misconfigured? The workflow MUST fail fast with clear error messages indicating which secret is missing.
- What happens if OCI CLI token expires during CI/CD? The workflow MUST use service account authentication (OIDC or API key) that does not expire during a pipeline run.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST deploy on an Oracle OKE cluster using only Always Free tier resources (VM.Standard.A1.Flex shape, 4 OCPUs, 24GB RAM total).
- **FR-002**: The system MUST install Dapr runtime on the OKE cluster with all system components healthy.
- **FR-003**: The system MUST deploy all 5 Dapr building blocks: Pub/Sub (pubsub.kafka), State Store (state.postgresql), Jobs API, Secrets (secretstores.kubernetes), and Service Invocation.
- **FR-004**: The system MUST connect to Redpanda Cloud serverless Kafka using SASL/SCRAM authentication through the Dapr pubsub component.
- **FR-005**: The system MUST store Kafka credentials and API keys as Kubernetes secrets, never in Helm values or environment variables directly.
- **FR-006**: The system MUST deploy the application via Helm using a cloud-specific values override file (`values-cloud.yaml`) layered on the existing Part B base chart.
- **FR-007**: The system MUST expose the frontend via a LoadBalancer service with a publicly routable IP address.
- **FR-008**: The system MUST NOT expose the backend API directly to the public internet; backend access MUST be internal (ClusterIP or Dapr service invocation).
- **FR-009**: The system MUST include a GitHub Actions workflow that builds Docker images, pushes to a container registry, and deploys to OKE on push to the main or deploy branch.
- **FR-010**: The system MUST push Docker images to either Oracle OCIR (free) or GitHub Container Registry (free for public repos).
- **FR-011**: The system MUST maintain full backward compatibility with Phase III chatbot, Phase IV local deployment, and Phase V Part A/B features.
- **FR-012**: The system MUST publish task lifecycle events (created, updated, completed, deleted) to Redpanda Cloud Kafka via Dapr Pub/Sub in CloudEvents 1.0 format.
- **FR-013**: The system MUST support Dapr Jobs API for scheduling reminder callbacks.
- **FR-014**: The system MUST provide accessible pod and Dapr sidecar logs via `kubectl logs`.
- **FR-015**: The system MUST include comprehensive deployment documentation covering Oracle signup, OKE creation, Dapr/Kafka configuration, CI/CD setup, public URL, and $0 cost confirmation.

### Key Entities

- **OKE Cluster**: Oracle Kubernetes Engine cluster with Always Free shape, node pool configuration, and kubectl access.
- **Dapr Components**: Set of Dapr building block configurations (pubsub, statestore, secretstore, jobs) deployed as Kubernetes custom resources.
- **Redpanda Cloud Cluster**: Serverless Kafka-compatible cluster with bootstrap URL, SASL credentials, and topics (task-events, reminders, task-updates).
- **CI/CD Pipeline**: GitHub Actions workflow with triggers, build/push/deploy steps, and secret references.
- **Cloud Values Override**: Helm values-cloud.yaml file containing cloud-specific image registries, replica counts, resource limits, and Kafka broker URLs.

### Assumptions

- The developer has an Oracle Cloud account with Always Free tier access (signup requires credit card but does not charge).
- The developer has a Redpanda Cloud account with a serverless cluster on the free tier.
- The developer has a GitHub repository with push access to the main/deploy branch.
- The existing Part B Helm chart structure is functional and follows the `helm/todo-app/` layout documented in the Part B spec.
- Docker images from Phase IV/Part B build correctly for ARM64 (Oracle Always Free uses ARM-based Ampere A1 processors).
- Neon PostgreSQL is accessible from the OKE cluster (no IP whitelisting issues).

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Application is accessible from any internet-connected browser via the LoadBalancer IP within 15 minutes of Helm deployment.
- **SC-002**: All application pods (frontend, backend) report Running with 2/2 containers (app + Dapr sidecar) and zero restarts for at least 10 minutes after deployment.
- **SC-003**: Task events appear in Redpanda Cloud console within 5 seconds of task creation via the chatbot.
- **SC-004**: A code push to the deploy branch triggers a GitHub Actions workflow that completes build, push, and deploy within 15 minutes.
- **SC-005**: The complete cloud deployment uses $0.00 in Oracle Cloud charges (confirmed via OCI billing dashboard).
- **SC-006**: A new developer can reproduce the setup by following the documentation in under 60 minutes (excluding Oracle account creation wait time).
- **SC-007**: 100% of Phase V Part A features (priorities, tags, recurring tasks, search/filter, chatbot intents) function identically on cloud as they do locally.
- **SC-008**: Dapr sidecar logs on the backend pod show successful component initialization for all 5 building blocks within 2 minutes of pod start.
- **SC-009**: At least 3 Kafka topics (task-events, reminders, task-updates) are created and accessible in Redpanda Cloud.
- **SC-010**: The GitHub Actions workflow file passes a dry-run lint check with no errors.

---

## Technical Architecture

### Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│                    ORACLE OKE CLUSTER (Always Free)                   │
│                  VM.Standard.A1.Flex (ARM64 / Ampere)                │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  DAPR SYSTEM (dapr-system ns)                  │   │
│  │  ┌──────────┐  ┌───────────────┐  ┌─────────────────────┐    │   │
│  │  │ Operator │  │ Sidecar       │  │ Placement / Sentry  │    │   │
│  │  │          │  │ Injector      │  │                     │    │   │
│  │  └──────────┘  └───────────────┘  └─────────────────────┘    │   │
│  └───────────────────────────────────────────────────────────────┘   │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐   │
│  │                  APPLICATION (default ns)                      │   │
│  │                                                                │   │
│  │  ┌──────────────────────┐    ┌──────────────────────┐         │   │
│  │  │   todo-frontend      │    │   todo-backend       │         │   │
│  │  │  ┌───────┬────────┐  │    │  ┌───────┬────────┐  │         │   │
│  │  │  │ Next  │ Dapr   │  │    │  │ Fast  │ Dapr   │  │         │   │
│  │  │  │ .js   │Sidecar │  │    │  │ API   │Sidecar │  │         │   │
│  │  │  │ :3000 │ :3500  │  │    │  │ :8000 │ :3500  │  │         │   │
│  │  │  └───────┴────────┘  │    │  └───────┴────────┘  │         │   │
│  │  │  Service: LB (pub)   │    │  Service: ClusterIP  │         │   │
│  │  └──────────────────────┘    └───────────┬──────────┘         │   │
│  │                                           │                    │   │
│  │  ┌────────────────────────────────────────┼───────────────┐   │   │
│  │  │              DAPR COMPONENTS           │               │   │   │
│  │  │  ┌──────────────┐ ┌──────────────┐ ┌──┴───────────┐   │   │   │
│  │  │  │ kafka-pubsub │ │  statestore  │ │ k8s-secrets  │   │   │   │
│  │  │  │(pubsub.kafka)│ │(state.pg)    │ │(secretstore) │   │   │   │
│  │  │  └──────┬───────┘ └──────┬───────┘ └──────────────┘   │   │   │
│  │  └─────────┼────────────────┼─────────────────────────────┘   │   │
│  └────────────┼────────────────┼─────────────────────────────────┘   │
│               │                │                                      │
└───────────────┼────────────────┼──────────────────────────────────────┘
                │                │
      ┌─────────▼──────┐  ┌─────▼──────────────┐
      │ REDPANDA CLOUD │  │  NEON PostgreSQL   │
      │  (Serverless)  │  │ (External DB)      │
      │ task-events    │  │                    │
      │ reminders      │  │                    │
      │ task-updates   │  │                    │
      └────────────────┘  └────────────────────┘

      ┌────────────────────────────────────────┐
      │         GITHUB ACTIONS CI/CD           │
      │  Push → Build → Push Image → Deploy   │
      │  Registry: OCIR / ghcr.io             │
      └────────────────────────────────────────┘
```

### Component Specifications

#### Dapr Components

| Component | Type | Cloud Configuration |
|-----------|------|---------------------|
| kafka-pubsub | pubsub.kafka | Redpanda Cloud broker with SASL/SCRAM |
| statestore | state.postgresql | Neon DB connection (external) |
| kubernetes-secrets | secretstores.kubernetes | OKE cluster K8s secrets |
| jobs-scheduler | jobs | HTTP callback to backend |

#### Kafka Topics

| Topic | Purpose | Events |
|-------|---------|--------|
| task-events | Task lifecycle | created, updated, completed, deleted |
| reminders | Scheduling | reminder.due, recurring.triggered |
| task-updates | State changes | status.changed, priority.changed |

#### Helm Values Override Strategy

```
helm/todo-app/
├── values.yaml              # Base values (from Part B)
├── values-local.yaml        # Minikube overrides (Part B)
└── values-cloud.yaml        # OKE cloud overrides (Part C) ← NEW
```

---

## Constraints

| Constraint | Description | Rationale |
|------------|-------------|-----------|
| Oracle Always Free only | 4 OCPUs, 24GB RAM (A1.Flex ARM64) | Zero ongoing cost |
| ARM64 images required | Ampere A1 is ARM-based | Multi-arch Docker builds needed |
| Redpanda Cloud free tier | 1GB storage, limited throughput | No self-hosted Kafka ops |
| No Ingress/TLS | Simple LoadBalancer for frontend | Reduce complexity for demo |
| No custom domain | Use LoadBalancer IP for demo | Free tier scope |
| No multi-region HA | Single region, single node pool | Free tier scope |
| GitHub Actions only | No ArgoCD, Jenkins, or Flux | Simplicity for hackathon |
| Secrets in K8s secrets | Not OCI Vault | Simpler, free, Dapr-compatible |

---

## Dependencies

### Prerequisites

- Phase V Part A code complete and all 96 tests passing
- Phase V Part B Helm charts and Dapr component templates available
- Docker installed locally for multi-arch image builds
- Oracle Cloud account (Always Free) created and active
- Redpanda Cloud account with serverless cluster created
- GitHub repository with Actions enabled

### External Services

- Neon PostgreSQL (existing, carried from Phase III)
- Redpanda Cloud serverless (new, free tier)
- Oracle Cloud Infrastructure (new, Always Free)
- GitHub Actions (existing, free for public repos)

---

## Risks & Mitigations

| Risk | Impact | Likelihood | Mitigation |
|------|--------|------------|------------|
| OKE Always Free shape insufficient for Dapr overhead | Pods OOMKilled or pending | Medium | Optimize resource requests/limits; reduce Dapr log level to "warn" |
| ARM64 Docker image build issues | Images won't run on A1 | Medium | Use multi-platform Docker buildx with `--platform linux/arm64` |
| Redpanda Cloud connectivity from OKE | Events not flowing | Low | Verify OCI security lists allow outbound 9092; test with curl from pod |
| OCI LoadBalancer IP assignment delay | App unreachable | Low | Document wait procedure; poll with `kubectl get svc -w` |
| GitHub Actions OKE auth expires | CI/CD fails | Medium | Use OCI OIDC provider or long-lived API key with proper rotation |
| Free tier resource exhaustion | Cluster becomes unhealthy | Low | Monitor resource usage; set resource requests/limits conservatively |

---

## Non-Goals (Out of Scope)

- Advanced monitoring stack (Prometheus + Grafana)
- Ingress controller with TLS termination
- Custom domain name configuration
- Multi-region or multi-zone high availability
- Kafka consumer services (event consumers are future work)
- Auto-scaling beyond Always Free limits
- Production-grade backup/disaster recovery

---

## References

- [Oracle Cloud Always Free](https://www.oracle.com/cloud/free/)
- [OKE Documentation](https://docs.oracle.com/en-us/iaas/Content/ContEng/home.htm)
- [Dapr Documentation](https://docs.dapr.io)
- [Redpanda Cloud](https://redpanda.com/redpanda-cloud)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Phase V Part B Spec](../006-phase5-partb-local-deployment/spec.md)
- [Phase V Part A Spec](../005-phase5-parta-advanced-events/spec.md)
- [Constitution v5.0.0](../../.specify/memory/constitution.md)
