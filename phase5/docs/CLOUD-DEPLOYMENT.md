# Cloud Deployment Guide: Phase V Part C - Oracle OKE

**Cost: $0.00** | Oracle Cloud Always Free + Redpanda Cloud Free Tier

Deploy the AI-Powered Todo Chatbot to Oracle Cloud Infrastructure (OCI) Kubernetes Engine (OKE) with Dapr sidecars, Redpanda Cloud Kafka, and GitHub Actions CI/CD.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Oracle Cloud Signup & OKE Cluster](#2-oracle-cloud-signup--oke-cluster)
3. [Redpanda Cloud Setup](#3-redpanda-cloud-setup)
4. [Docker Multi-Arch Image Build](#4-docker-multi-arch-image-build)
5. [Helm Cloud Deployment](#5-helm-cloud-deployment)
6. [CI/CD Pipeline (GitHub Actions)](#6-cicd-pipeline-github-actions)
7. [Monitoring & Logging](#7-monitoring--logging)
8. [Troubleshooting](#8-troubleshooting)
9. [Cost Report](#9-cost-report)
10. [Public Demo URL](#10-public-demo-url)

---

## 1. Prerequisites

### Accounts Required

| Account | URL | Cost |
|---------|-----|------|
| Oracle Cloud (Always Free) | https://www.oracle.com/cloud/free/ | Free (credit card required, not charged) |
| Redpanda Cloud | https://redpanda.com/cloud | Free tier |
| GitHub | https://github.com | Free for public repos |
| Neon PostgreSQL | https://neon.tech | Free tier (from Phase III) |
| Cohere | https://dashboard.cohere.com | Free tier (from Phase III) |

### CLI Tools Required

```bash
# OCI CLI
pip install oci-cli
oci --version

# kubectl
kubectl version --client

# Helm 3.x
helm version

# Docker with buildx
docker buildx version

# Dapr CLI
dapr --version
```

---

## 2. Oracle Cloud Signup & OKE Cluster

### 2.1 Create Oracle Cloud Account

1. Visit https://www.oracle.com/cloud/free/
2. Sign up with email (credit card required, not charged)
3. Choose a home region (e.g., `us-ashburn-1`)
4. Wait for account activation (~5 minutes)

### 2.2 Create OKE Cluster

1. Login to Oracle Cloud Console
2. Navigate: **Developer Services** -> **Kubernetes Clusters (OKE)**
3. Click **Create Cluster** -> **Quick Create**
4. Configure:
   - **Name**: `todo-chatbot-cluster`
   - **Kubernetes Version**: 1.28+
   - **Shape**: VM.Standard.A1.Flex (Always Free, ARM64)
   - **OCPUs per node**: 2
   - **Memory per node**: 12 GB
   - **Number of nodes**: 2
5. Click **Create** (takes ~10 minutes)

**Total resources**: 4 OCPUs, 24 GB RAM (within Always Free limits)

### 2.3 Configure kubectl

```bash
# Install OCI CLI config
oci setup config

# Download kubeconfig
oci ce cluster create-kubeconfig \
  --cluster-id <CLUSTER_OCID> \
  --file $HOME/.kube/config \
  --region <REGION> \
  --token-version 2.0.0

# Verify
kubectl get nodes
# Expected: 2 nodes, Ready, architecture: arm64
```

### 2.4 Install Dapr on OKE

```bash
dapr init -k --wait
dapr status -k
# Expected: All components healthy (operator, sidecar-injector, placement, sentry)
```

---

## 3. Redpanda Cloud Setup

### 3.1 Create Serverless Cluster

1. Login to https://cloud.redpanda.com
2. Create a **Serverless** cluster (free tier)
3. Choose closest region to your OKE cluster
4. Note the **Bootstrap URL** (e.g., `xyz.any.us-east-1.mpx.prd.cloud.redpanda.com:9092`)

### 3.2 Create SASL Credentials

1. In Redpanda Console, go to **Security** -> **Users**
2. Create a user with SCRAM-SHA-256 mechanism
3. Note **username** and **password**

### 3.3 Create Topics

Create these topics in the Redpanda Console (1 partition each):

| Topic | Purpose |
|-------|---------|
| `task-events` | Task lifecycle events (created, updated, completed, deleted) |
| `reminders` | Scheduling events (reminder.due, recurring.triggered) |
| `task-updates` | State change events (status.changed, priority.changed) |

### 3.4 Create Kubernetes Secrets

```bash
# Kafka credentials
kubectl create secret generic kafka-secrets \
  --from-literal=username=<REDPANDA_USER> \
  --from-literal=password=<REDPANDA_PASSWORD>

# Application secrets
kubectl create secret generic todo-secrets \
  --from-literal=database-url=<NEON_URL> \
  --from-literal=cohere-api-key=<COHERE_KEY> \
  --from-literal=jwt-secret=<JWT_SECRET>

# Verify
kubectl get secrets
```

---

## 4. Docker Multi-Arch Image Build

OKE Always Free uses ARM64 (Ampere A1) processors. Images must support both ARM64 (cloud) and AMD64 (local dev).

### 4.1 Setup Buildx

```bash
docker buildx create --name multiarch --use
docker buildx inspect --bootstrap
```

### 4.2 Login to GitHub Container Registry

```bash
# Create a GitHub Personal Access Token with write:packages scope
docker login ghcr.io -u <GITHUB_USERNAME> -p <GITHUB_TOKEN>
```

### 4.3 Build & Push Images

```bash
cd phase5/

# Backend (ARM64 + AMD64)
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.backend \
  -t ghcr.io/<OWNER>/todo-backend:latest --push .

# Frontend (ARM64 + AMD64)
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.frontend \
  -t ghcr.io/<OWNER>/todo-frontend:latest --push .
```

### 4.4 Verify

Check images at `https://github.com/<OWNER>?tab=packages` — both should show multi-platform manifests.

---

## 5. Helm Cloud Deployment

### 5.1 Deploy with Cloud Values

```bash
cd phase5/

helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values.yaml \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  --set kafka.brokerUrl="<REDPANDA_BOOTSTRAP_URL>:9092" \
  --set secrets.databaseUrl="<NEON_URL>" \
  --set secrets.cohereApiKey="<COHERE_KEY>" \
  --set secrets.jwtSecret="<JWT_SECRET>"
```

Or use the deploy script:

```bash
# Linux/Mac
./scripts/deploy-cloud.sh \
  --broker-url "<REDPANDA_URL>:9092" \
  --database-url "<NEON_URL>" \
  --cohere-key "<COHERE_KEY>" \
  --jwt-secret "<JWT_SECRET>"
```

```powershell
# Windows
.\scripts\deploy-cloud.ps1 `
  -BrokerUrl "<REDPANDA_URL>:9092" `
  -DatabaseUrl "<NEON_URL>" `
  -CohereKey "<COHERE_KEY>" `
  -JwtSecret "<JWT_SECRET>"
```

### 5.2 Verify Deployment

```bash
# Check pods (expect 2/2 containers = app + Dapr sidecar)
kubectl get pods

# Check services (frontend should have EXTERNAL-IP)
kubectl get svc

# Wait for LoadBalancer IP
kubectl get svc -w
```

### 5.3 Access Application

```
http://<EXTERNAL-IP>:3000
```

Login, create tasks via chatbot, verify all Phase V Part A features work.

### 5.4 Values Override Strategy

```
values.yaml           Base values (Part B, disabled Dapr/Kafka)
  └── values-dapr.yaml    Part B local (Dapr + local Redpanda)
  └── values-cloud.yaml   Part C cloud (Dapr + Redpanda Cloud + LoadBalancer)
```

---

## 6. CI/CD Pipeline (GitHub Actions)

### 6.1 Workflow File

The CI/CD pipeline is at `.github/workflows/deploy-cloud.yml`. It triggers on push to `main` or `deploy` branches (paths: `phase5/**`).

**Pipeline steps**: Checkout -> Buildx -> ghcr.io Login -> Build+Push Backend -> Build+Push Frontend -> OCI CLI Setup -> kubectl Config -> Helm Deploy -> Verify

### 6.2 Required GitHub Secrets

Configure these 12 secrets in your GitHub repository settings:

| Secret | Source |
|--------|--------|
| `OCI_CLI_USER` | Oracle Cloud Console -> User OCID |
| `OCI_CLI_TENANCY` | Oracle Cloud Console -> Tenancy OCID |
| `OCI_CLI_FINGERPRINT` | OCI API Key fingerprint |
| `OCI_CLI_KEY_CONTENT` | Base64-encoded OCI API private key (`base64 ~/.oci/oci_api_key.pem`) |
| `OCI_CLI_REGION` | e.g., `us-ashburn-1` |
| `OKE_CLUSTER_OCID` | OKE Cluster OCID from Console |
| `DATABASE_URL` | Neon PostgreSQL connection string |
| `COHERE_API_KEY` | Cohere API key |
| `JWT_SECRET` | JWT signing secret |
| `KAFKA_BROKER_URL` | Redpanda Cloud bootstrap URL |
| `KAFKA_USERNAME` | Redpanda SASL username |
| `KAFKA_PASSWORD` | Redpanda SASL password |

### 6.3 Trigger Deployment

```bash
git push origin deploy
# Or merge to main
```

Monitor at: `https://github.com/<OWNER>/<REPO>/actions`

---

## 7. Monitoring & Logging

### Application Logs

```bash
# Backend application logs
kubectl logs <backend-pod> -c todo-backend

# Backend Dapr sidecar logs
kubectl logs <backend-pod> -c daprd

# Frontend application logs
kubectl logs <frontend-pod> -c todo-frontend

# Frontend Dapr sidecar logs
kubectl logs <frontend-pod> -c daprd

# Follow logs in real-time
kubectl logs -f <pod-name> -c <container-name>
```

### Dapr Component Status

Check Dapr sidecar logs for component initialization:
```bash
kubectl logs <backend-pod> -c daprd | grep "component"
# Expected: kafka-pubsub, statestore, kubernetes-secrets initialized
```

### OCI Monitoring

1. Oracle Cloud Console -> **Observability & Management** -> **Monitoring**
2. View node CPU, memory, network metrics
3. View pod health and restart counts

### Redpanda Cloud Console

1. Login to https://cloud.redpanda.com
2. Navigate to your cluster -> **Topics**
3. View messages in `task-events`, `reminders`, `task-updates`
4. Verify CloudEvents 1.0 format in message payloads

---

## 8. Troubleshooting

### Pods not starting (Pending/CrashLoopBackOff)

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check if resources are sufficient
kubectl top nodes

# Check image pull issues
kubectl get events --sort-by='.lastTimestamp'
```

### LoadBalancer IP not assigned

```bash
# Wait and watch
kubectl get svc -w

# Check OCI service limits
# Console -> Governance -> Limits, Quotas and Usage -> LB
```

### Dapr sidecar not connecting to Kafka

```bash
# Check sidecar logs for Kafka errors
kubectl logs <backend-pod> -c daprd | grep -i "kafka\|error\|pubsub"

# Verify Kafka connectivity from pod
kubectl exec <backend-pod> -c todo-backend -- curl -v telnet://<REDPANDA_URL>:9092
```

### GitHub Actions failing

- Check that all 12 secrets are configured correctly
- Verify OCI API key is base64-encoded: `base64 -w0 ~/.oci/oci_api_key.pem`
- Verify OKE cluster OCID matches your cluster

### Image pull errors

```bash
# For private ghcr.io repos, create pull secret
kubectl create secret docker-registry ghcr-pull-secret \
  --docker-server=ghcr.io \
  --docker-username=<GITHUB_USER> \
  --docker-password=<GITHUB_TOKEN>
```

---

## 9. Cost Report

| Resource | Provider | Tier | Monthly Cost |
|----------|----------|------|--------------|
| OKE Cluster (2 nodes, A1.Flex) | Oracle Cloud | Always Free | $0.00 |
| LoadBalancer (10 Mbps) | Oracle Cloud | Always Free | $0.00 |
| Block Storage (50 GB) | Oracle Cloud | Always Free | $0.00 |
| Kafka (Serverless) | Redpanda Cloud | Free Tier | $0.00 |
| PostgreSQL | Neon | Free Tier | $0.00 |
| Container Registry | GitHub (ghcr.io) | Free (public) | $0.00 |
| CI/CD Pipeline | GitHub Actions | Free (public) | $0.00 |
| AI API | Cohere | Free Tier | $0.00 |
| **Total** | | | **$0.00** |

Verify in OCI Console: **Governance** -> **Cost Analysis** -> Confirm $0.00

---

## 10. Public Demo URL

After deployment, the application is accessible at:

```
http://<LOADBALANCER_EXTERNAL_IP>:3000
```

To get the URL:
```bash
kubectl get svc todo-chatbot-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

### Features Available

- Task CRUD via AI chatbot (Cohere-powered)
- Priority levels (high/medium/low)
- Tags and categories
- Recurring tasks (daily/weekly/monthly)
- Search, filter, and sort
- Event-driven architecture (Dapr Pub/Sub -> Redpanda Cloud)
- Real-time event streaming to Kafka topics
