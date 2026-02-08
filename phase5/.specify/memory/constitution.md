<!--
╔══════════════════════════════════════════════════════════════════════════════╗
║                           SYNC IMPACT REPORT                                   ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ Version Change: v4.0.0 → v5.0.0 (MAJOR)                                      ║
║ Rationale: Phase transition from local Minikube to cloud K8s (AKS/GKE/DOKS) ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ MODIFIED PRINCIPLES:                                                          ║
║ - "AI-Assisted Infrastructure Only" → expanded for cloud CLI agents           ║
║ - "Backward Compatibility" → now includes Part B local deployment             ║
║ - "Full Dapr Runtime" → cloud Dapr with external Kafka/secrets                ║
║ - "Local Kafka" → "Kafka via Redpanda Cloud / Confluent / Strimzi"           ║
║ - "Extend Phase IV Helm Charts" → "Extend Part B Helm Charts for Cloud"      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ ADDED SECTIONS:                                                               ║
║ + Cloud Provider Selection & Free Tier Guidance                              ║
║ + CI/CD Pipeline (GitHub Actions)                                            ║
║ + External Kafka Options (Redpanda Cloud, Confluent, self-hosted)            ║
║ + Public Access & Ingress                                                    ║
║ + Cost Control & Budget Guardrails                                           ║
║ + Monitoring & Logging Basics                                                ║
║ + Demo Video Requirements                                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ REMOVED SECTIONS:                                                             ║
║ - Minikube Cluster Standards (Part B - complete, still supported)            ║
║ - Local-only Kafka constraints (now cloud Kafka)                             ║
║ - "No consumer pods" constraint (removed)                                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ TEMPLATES STATUS:                                                             ║
║ - plan-template.md: ✅ Reviewed - Constitution Check section compatible      ║
║ - spec-template.md: ✅ Reviewed - Success Criteria section compatible        ║
║ - tasks-template.md: ✅ Reviewed - Phase structure compatible                ║
╠══════════════════════════════════════════════════════════════════════════════╣
║ FOLLOW-UP TODOs: None                                                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
-->

# Project Constitution

**Project**: Hackathon II: Evolution of Todo
**Phase**: V – Part C: Production-Grade Cloud Deployment (AKS / GKE / DOKS / OKE)
**Version**: 5.0.0
**Ratification Date**: 2026-01-22
**Last Amended**: 2026-02-06

---

## 1. Mission Statement

Deploy the complete AI-Powered Todo Chatbot (with all Phase III chatbot, Phase IV local K8s, Part A advanced features, and Part B Dapr/Kafka patterns) to a production-grade cloud Kubernetes cluster with full Dapr runtime, cloud Kafka, CI/CD pipeline, public access, and monitoring. The application code and Dapr patterns are complete from Parts A and B—this phase focuses on cloud infrastructure, external access, CI/CD automation, and production readiness.

---

## 2. Core Principles

### Principle 1: Spec-Driven Development

**Statement**: No cloud resource, Helm change, Dapr component, CI/CD step, or infrastructure change without approved spec/task reference.

**Rationale**: All cloud deployment artifacts MUST be traceable to specifications. Every cloud cluster setting, Helm override value, Dapr cloud component, CI/CD workflow step, and DNS/Ingress configuration references a spec file or task ID.

### Principle 2: AI-Assisted Infrastructure Only

**Statement**: No manual kubectl/helm/doctl/az/gcloud commands—use AI agents (kubectl-ai, kagent, HelmAgent, CloudDeployAgent) for all operations whenever possible.

**Rationale**: The hackathon emphasizes AI-assisted operations. Manual commands bypass the agent orchestration that demonstrates AIOps proficiency. Cloud-specific CLIs (doctl, az, gcloud, oci) MUST be invoked through agent workflows, not ad-hoc shell sessions.

### Principle 3: Backward Compatibility Mandatory

**Statement**: Phase III chatbot, Phase IV local deployment, Phase V Part A features, and Phase V Part B Dapr/Kafka patterns MUST remain fully functional in the cloud deployment.

**Rationale**: Each phase builds upon the previous. Breaking existing functionality invalidates prior work and fails integration requirements. Cloud deployment MUST NOT alter application behavior—only the infrastructure target changes.

### Principle 4: Full Dapr Runtime on Cloud

**Statement**: Use all 5 Dapr building blocks on cloud: Pub/Sub (pubsub.kafka), State Store (state.postgresql), Jobs API (for reminders), Secrets (secretstores.kubernetes or cloud secret manager), and Service Invocation.

**Rationale**: Demonstrating the full Dapr capability set on a production cloud cluster maximizes hackathon bonus points and proves mastery of distributed application patterns at scale.

### Principle 5: Dapr-Exclusive Distributed Concerns

**Statement**: Use Dapr exclusively for distributed concerns—no direct Kafka client, no polling, no manual infrastructure coupling in application code.

**Rationale**: Dapr provides a consistent abstraction layer. The same application code from Part B MUST work on cloud Kafka without modification. Direct infrastructure coupling defeats the purpose of Dapr and complicates cloud migration.

### Principle 6: Cloud Kafka via Managed Service or Strimzi

**Statement**: Connect to Kafka using one of: Redpanda Cloud serverless (free tier, recommended), Confluent Cloud ($400 credit), or self-hosted Strimzi operator on cluster.

**Rationale**: Cloud Kafka demonstrates the full event-driven architecture with production-grade messaging. Redpanda Cloud serverless is recommended for zero-ops; Strimzi for teams wanting full control. Dapr abstraction ensures the application code is identical regardless of Kafka provider.

### Principle 7: Extend Part B Helm Charts for Cloud

**Statement**: Extend existing Part B Helm charts with cloud-specific values overrides (values-cloud.yaml) rather than creating new charts.

**Rationale**: Reusing existing Helm infrastructure reduces complexity, maintains consistency, and demonstrates that the same charts work across local Minikube and cloud clusters with only values changes.

### Principle 8: Cost Control as Non-Negotiable

**Statement**: Use ONLY free credits and always-free tiers. Document every resource cost. Total spend MUST be $0 for the demo.

**Rationale**: Hackathon projects MUST demonstrate cost-awareness. Free tier options exist for every component: DigitalOcean ($200/60d), Azure ($200/30d), Google ($300/90d), Oracle (Always Free OKE). Going beyond free tier is unnecessary and wasteful.

### Principle 9: CI/CD Pipeline Required

**Statement**: A GitHub Actions workflow MUST build Docker images, push to container registry, and deploy to the cloud cluster on push to main/deploy branch.

**Rationale**: Production-grade deployment requires automated pipelines. Manual `helm upgrade` on cloud is error-prone and not demonstrable in a hackathon video. CI/CD proves end-to-end automation proficiency.

---

## 3. Cloud Provider Selection

### 3.1 Provider Options

| Provider | Credit | Duration | Recommendation |
|----------|--------|----------|----------------|
| DigitalOcean DOKS | $200 | 60 days (or 1yr GitHub Student) | Good for simplicity |
| Azure AKS | $200 | 30 days + free services | Good for enterprise features |
| Google GKE | $300 | 90 days | Good for GKE Autopilot |
| Oracle OKE | Always Free | Unlimited (4 OCPUs, 24GB RAM) | Best for long-term learning |

### 3.2 Cluster Requirements

| Setting | Minimum Value |
|---------|---------------|
| Nodes | 2 (for HA) |
| Node Size | 2 vCPU, 4GB RAM each |
| Kubernetes Version | 1.28+ |
| Region | Closest to user |
| Addons | Ingress Controller, Metrics |

### 3.3 Container Registry

| Provider | Registry |
|----------|----------|
| DigitalOcean | DigitalOcean Container Registry (DOCR) |
| Azure | Azure Container Registry (ACR) |
| Google | Google Artifact Registry (GAR) |
| Oracle | Oracle Container Registry (OCIR) |
| Alternative | GitHub Container Registry (ghcr.io) — free for public |

---

## 4. Dapr on Cloud

### 4.1 Installation

**Command** (via kubectl-ai/kagent):
```bash
dapr init -k --wait
```

**Verification**:
```bash
dapr status -k
kubectl get pods -n dapr-system
```

### 4.2 Required Dapr Components

| Component | Type | Cloud Configuration |
|-----------|------|---------------------|
| kafka-pubsub | pubsub.kafka | Redpanda Cloud / Confluent / Strimzi broker |
| statestore | state.postgresql | Neon DB connection (external, same as local) |
| jobs-scheduler | jobs | HTTP callback to backend service |
| kubernetes-secrets | secretstores.kubernetes | Cloud cluster K8s secrets |

### 4.3 Cloud Pub/Sub Component Example

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kafka-pubsub
  namespace: default
spec:
  type: pubsub.kafka
  version: v1
  metadata:
    - name: brokers
      value: "<CLOUD_KAFKA_BROKER>:9092"
    - name: consumerGroup
      value: "todo-app"
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
auth:
  secretStore: kubernetes-secrets
```

### 4.4 Sidecar Injection

All cloud deployments MUST include Dapr annotations:

```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"
  dapr.io/app-port: "<port>"
  dapr.io/log-level: "info"
  dapr.io/enable-api-logging: "true"
```

---

## 5. Kafka Options for Cloud

### 5.1 Option 1: Redpanda Cloud Serverless (Recommended)

- Free tier: 1 GB storage, 10 MB/s throughput
- Zero ops—no cluster to manage
- SASL/SCRAM authentication
- Topics: task-events, reminders, task-updates

### 5.2 Option 2: Confluent Cloud

- $400 credit available
- Fully managed Kafka
- Schema Registry included
- API key authentication

### 5.3 Option 3: Self-Hosted Strimzi on Cloud Cluster

- Deploy Strimzi operator on cloud K8s
- Full control, no external dependency
- Consumes cluster compute resources
- Single-broker for demo (ephemeral storage OK)

### 5.4 Topics

| Topic | Purpose | Partitions |
|-------|---------|------------|
| task-events | Task lifecycle events (CRUD) | 1 (demo) |
| reminders | Reminder/recurring triggers | 1 (demo) |
| task-updates | State change notifications | 1 (demo) |

---

## 6. Helm Chart Cloud Extensions

### 6.1 Values Override Strategy

```text
helm/todo-app/
├── values.yaml              # Base values (from Part B)
├── values-local.yaml        # Minikube overrides (Part B)
└── values-cloud.yaml        # Cloud overrides (Part C) ← NEW
```

### 6.2 Cloud Values Example (values-cloud.yaml)

```yaml
# Cloud-specific overrides
global:
  environment: production
  cloudProvider: digitalocean  # or azure, google, oracle

backend:
  replicas: 2
  image:
    registry: registry.digitalocean.com/todo-app
    tag: latest
  resources:
    requests:
      memory: 256Mi
      cpu: 250m
    limits:
      memory: 512Mi
      cpu: 500m

frontend:
  replicas: 2
  image:
    registry: registry.digitalocean.com/todo-app
    tag: latest
  service:
    type: LoadBalancer  # or use Ingress

dapr:
  enabled: true
  logLevel: info

kafka:
  enabled: true
  external: true
  brokerUrl: "<REDPANDA_CLOUD_URL>:9092"
```

### 6.3 Deployment Command

```bash
# Via HelmAgent / kubectl-ai:
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/todo-app/values.yaml \
  -f ./helm/todo-app/values-cloud.yaml \
  --set backend.image.tag=$IMAGE_TAG
```

---

## 7. CI/CD Pipeline

### 7.1 GitHub Actions Workflow

```text
.github/workflows/
└── deploy-cloud.yml    # Build → Push → Deploy
```

### 7.2 Pipeline Steps

1. **Trigger**: Push to `main` or `deploy` branch
2. **Build**: Docker build for backend and frontend
3. **Push**: Push images to container registry
4. **Deploy**: `helm upgrade --install` on cloud cluster
5. **Verify**: Health check on deployed services

### 7.3 Secrets Required in GitHub

| Secret | Purpose |
|--------|---------|
| KUBE_CONFIG | Base64-encoded kubeconfig for cloud cluster |
| REGISTRY_TOKEN | Container registry authentication |
| DATABASE_URL | Neon PostgreSQL connection string |
| COHERE_API_KEY | Cohere AI API key |
| KAFKA_USERNAME | Kafka/Redpanda SASL username |
| KAFKA_PASSWORD | Kafka/Redpanda SASL password |

---

## 8. Public Access & Ingress

### 8.1 Frontend Access

| Method | Use Case |
|--------|----------|
| LoadBalancer Service | Simplest—cloud assigns external IP |
| Ingress Controller | Domain-based routing (nginx-ingress) |
| NodePort + External DNS | Budget option |

### 8.2 Backend Access

Backend MUST NOT be publicly exposed directly. Frontend communicates via internal ClusterIP service or Dapr service invocation.

### 8.3 SSL/TLS (Optional Bonus)

- Let's Encrypt via cert-manager (free)
- Cloud-managed SSL (DigitalOcean, Azure, Google)

---

## 9. Monitoring & Logging

### 9.1 Required (Minimum)

| Tool | Purpose |
|------|---------|
| kubectl logs | Pod and Dapr sidecar logs |
| dapr dashboard | Dapr component health (if deployed) |
| Cloud provider monitoring | Basic node/pod metrics |

### 9.2 Optional (Bonus Points)

| Tool | Purpose |
|------|---------|
| Prometheus + Grafana | Metrics dashboards |
| DigitalOcean Monitoring | Built-in for DOKS |
| Azure Monitor | Built-in for AKS |
| Google Cloud Logging | Built-in for GKE |

---

## 10. Constraints

| Constraint | Rationale |
|------------|-----------|
| Free credits / always-free tiers only | No paid overage in demo |
| External Neon PostgreSQL continues | Dapr state for cache only |
| Public access via LoadBalancer or Ingress | App MUST be reachable from internet |
| Secrets via Dapr kubernetes-secrets or cloud secret store | Never hardcode |
| No vendor lock-in | Dapr abstracts Kafka/DB |
| Demo video required | Show cloud URL, features, events, CI/CD run |
| Part B local deployment MUST still work | Cloud is additive, not replacement |

---

## 11. Success Criteria (Part C Only)

### 11.1 Cloud Cluster

- [ ] Cloud cluster created (DOKS/AKS/GKE/OKE)
- [ ] kubectl configured and connected to cloud cluster
- [ ] Cluster has 2+ nodes with sufficient resources

### 11.2 Dapr on Cloud

- [ ] Dapr initialized on cloud cluster (`dapr status -k` healthy)
- [ ] All Dapr system pods running
- [ ] Dapr components deployed (pubsub, statestore, secrets)

### 11.3 Kafka on Cloud

- [ ] Kafka connected (Redpanda Cloud / Confluent / Strimzi)
- [ ] Topics created (task-events, reminders, task-updates)
- [ ] Events flowing through cloud Kafka

### 11.4 Helm Deployment

- [ ] Helm install with cloud values succeeds
- [ ] Dapr sidecars injected on all pods
- [ ] All pods reach Running state on cloud

### 11.5 Public Access

- [ ] App publicly accessible via external IP or domain
- [ ] Frontend loads in browser from public URL
- [ ] Full flow works: login → dashboard → chatbot → advanced features

### 11.6 CI/CD Pipeline

- [ ] GitHub Actions workflow file exists
- [ ] Pipeline triggers on push to main/deploy
- [ ] Builds Docker images and pushes to registry
- [ ] Deploys to cloud cluster automatically
- [ ] Show in demo video

### 11.7 Monitoring

- [ ] kubectl logs accessible for all pods
- [ ] Dapr sidecar logs show event publish/subscribe
- [ ] Basic cloud monitoring dashboard accessible

### 11.8 Documentation

- [ ] Cloud signup and credit activation steps
- [ ] Cluster creation commands/steps
- [ ] Helm values-cloud.yaml documented
- [ ] CI/CD workflow YAML documented
- [ ] Public demo URL recorded
- [ ] Cost report ($0 confirmed)

---

## 12. Non-Negotiables

1. **NEVER** hardcode secrets—use Dapr secrets or cloud secret store
2. **NEVER** expose sensitive env vars in Helm values or CI/CD logs
3. **NEVER** break Phase III/IV/Part A/Part B functionality
4. **NEVER** exceed free tier/credit limits—document all costs
5. **NEVER** expose backend directly to public internet
6. **NEVER** skip CI/CD—all deployments via pipeline after initial setup
7. **NEVER** use cloud credentials without proper secret management
8. **NEVER** commit cloud credentials or kubeconfig to git

---

## 13. Bonus Alignment

| Bonus Category | Part C Alignment |
|----------------|------------------|
| Full Dapr on Cloud | All 5 building blocks on production cluster |
| Cloud Kafka Integration | Redpanda Cloud / Confluent + Dapr Pub/Sub |
| AIOps Usage | kubectl-ai/kagent/CloudDeployAgent for operations |
| CI/CD Pipeline | GitHub Actions build → push → deploy |
| Production-Grade | HA replicas, LoadBalancer, secrets management |
| Multi-Environment | Same Helm chart: local (values-local) + cloud (values-cloud) |
| Event-Driven at Scale | Cloud Kafka proving distributed event architecture |
| Demo-Ready | Public URL accessible for hackathon video |

---

## 14. Governance

### 14.1 Amendment Procedure

1. Propose change via `/sp.constitution` command
2. Document rationale and impact
3. Update version according to semver:
   - MAJOR: Breaking changes or phase transitions
   - MINOR: New principles or sections
   - PATCH: Clarifications or fixes

### 14.2 Compliance Review

- All PRs MUST reference this constitution
- Success criteria used for acceptance testing
- Non-negotiables enforced in code review

---

## 15. Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-18 | Phase III: AI Todo Chatbot |
| 2.0.0 | 2026-01-22 | Phase IV: Local K8s Deployment |
| 3.0.0 | 2026-01-31 | Phase V Part A: Advanced Features & Event-Driven Logic |
| 4.0.0 | 2026-02-03 | Phase V Part B: Local Minikube + Dapr + Kafka Deployment |
| 5.0.0 | 2026-02-06 | Phase V Part C: Cloud Deployment (AKS/GKE/DOKS/OKE) + CI/CD |
