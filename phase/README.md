# 🤖 TaskFlow - AI-Powered Todo Chatbot

> **Phase IV: Local Kubernetes Deployment with AIOps**

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Kubernetes](https://img.shields.io/badge/K8s-Minikube-blue)
![Helm](https://img.shields.io/badge/Helm-v3-purple)
![Docker](https://img.shields.io/badge/Docker-Multi--Stage-blue)

---

## 🎯 Overview

This is Phase IV of the TaskFlow project - deploying the AI-Powered Todo Chatbot to a local Kubernetes cluster using Minikube and Helm Charts. This phase demonstrates cloud-native deployment practices with AIOps tools.

### Key Features
- 🐳 **Optimized Docker Images**: Multi-stage builds targeting <300MB combined
- ☸️ **Kubernetes Deployment**: Full-stack deployment on Minikube
- 📦 **Helm Charts**: Parameterized deployment configuration
- 🤖 **AIOps Integration**: Gordon AI, kubectl-ai, kagent usage
- 🔐 **Secure Secrets**: Kubernetes Secrets for sensitive data

---

## 📋 Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker Desktop | 29.1.3+ | Container runtime |
| Minikube | 1.37.0+ | Local Kubernetes cluster |
| kubectl | 1.35.0+ | Kubernetes CLI |
| Helm | 4.1.0+ | Kubernetes package manager |
| kubectl-ai | Latest | AI-assisted kubectl (optional) |
| kagent | Latest | K8s AI agent (optional) |

### Verify Prerequisites
```bash
docker --version     # Docker version 29.1.3
minikube version     # minikube version: v1.37.0
kubectl version --client  # Client Version: v1.35.0
helm version         # version.BuildInfo{Version:"v4.1.0"}
```

---

## 🚀 Quick Start

### Option 1: Automated Deployment
```bash
# Run the deployment script
./scripts/deploy.sh
```

### Option 2: Manual Deployment

#### 1. Start Minikube
```bash
minikube start --cpus=4 --memory=8192 --driver=docker
```

#### 2. Configure Docker for Minikube
```bash
# On Unix/Mac
eval $(minikube docker-env)

# On Windows PowerShell
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

#### 3. Build Docker Images
```bash
# Build backend image
docker build -t todo-backend:latest -f docker/Dockerfile.backend .

# Build frontend image
docker build -t todo-frontend:latest -f docker/Dockerfile.frontend .
```

#### 4. Create Kubernetes Secrets
```bash
kubectl create secret generic todo-chatbot-secrets \
  --from-literal=database-url="YOUR_NEON_DATABASE_URL" \
  --from-literal=cohere-api-key="YOUR_COHERE_API_KEY" \
  --from-literal=jwt-secret="YOUR_JWT_SECRET"
```

#### 5. Deploy with Helm
```bash
helm install todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-local.yaml
```

#### 6. Access Application
```bash
# Get frontend URL
minikube service todo-chatbot-frontend --url
```

---

## 🏗️ Project Structure

```
phase4_chatbot/
├── docker/
│   ├── Dockerfile.backend     # Optimized FastAPI image (<200MB)
│   ├── Dockerfile.frontend    # Optimized Next.js image (<100MB)
│   └── .dockerignore
├── helm/
│   └── todo-chatbot/
│       ├── Chart.yaml
│       ├── values.yaml
│       ├── values-local.yaml  # Minikube overrides
│       └── templates/
│           ├── _helpers.tpl
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── configmap.yaml
│           └── secret.yaml
├── scripts/
│   ├── deploy.sh              # Full deployment script
│   ├── verify.sh              # Health verification
│   └── cleanup.sh             # Resource cleanup
├── backend/                   # FastAPI application
├── frontend/                  # Next.js application
└── specs/                     # SDD specifications
```

---

## 🤖 AIOps Integration

### Gordon AI Usage (Docker)

Gordon AI was used for Dockerfile optimization:

**Prompt 1**: Backend Dockerfile
```
docker ai "create an optimized multi-stage Dockerfile for a FastAPI Python 3.11
application with asyncpg, sqlmodel, cohere. Target image size under 200MB. Use
python:3.11-slim base image."
```

**Prompt 2**: Frontend Dockerfile
```
docker ai "create minimal Next.js 15 standalone Dockerfile using node:18-alpine,
target <100MB with multi-stage build"
```

**Prompt 3**: Optimization
```
docker ai "optimize this Dockerfile to reduce layer count and improve caching"
```

### kubectl-ai Commands

AI-assisted Kubernetes operations:
```bash
# Scale deployment
kubectl ai "scale the todo-backend deployment to 2 replicas"

# Debug pods
kubectl ai "check why pods might be pending or failing"

# Generate resources
kubectl ai "generate helm deployment template for fastapi backend with port 8000"
```

### kagent Operations

Cluster health and optimization:
```bash
# Health analysis
kagent "analyze cluster health and resource usage"

# Optimization suggestions
kagent "suggest resource optimizations for the todo-chatbot deployment"
```

---

## 📊 Image Sizes

| Image | Target | Actual | Status |
|-------|--------|--------|--------|
| todo-frontend | <100MB | ~90MB | ✅ |
| todo-backend | <200MB | ~180MB | ✅ |
| **Combined** | <300MB | ~270MB | ✅ |

---

## 🔧 Configuration

### Environment Variables

**Backend (via ConfigMap/Secret):**
| Variable | Source | Description |
|----------|--------|-------------|
| HOST | ConfigMap | Server host (0.0.0.0) |
| PORT | ConfigMap | Server port (8000) |
| DEBUG | ConfigMap | Debug mode |
| CORS_ORIGINS | ConfigMap | Allowed origins |
| DATABASE_URL | Secret | Neon PostgreSQL URL |
| COHERE_API_KEY | Secret | Cohere API key |
| JWT_SECRET | Secret | JWT signing key |

**Frontend:**
| Variable | Source | Description |
|----------|--------|-------------|
| NODE_ENV | Deployment | Environment (production) |
| NEXT_PUBLIC_API_URL | Deployment | Backend service URL |

### Resource Limits

Both pods are configured with:
- **CPU Limit**: 500m
- **Memory Limit**: 512Mi
- **CPU Request**: 100m
- **Memory Request**: 256Mi

---

## 🔍 Verification

### Check Pod Status
```bash
kubectl get pods -l app.kubernetes.io/instance=todo-chatbot
```

### Check Services
```bash
kubectl get svc -l app.kubernetes.io/instance=todo-chatbot
```

### View Logs
```bash
kubectl logs -l app=todo-backend
kubectl logs -l app=todo-frontend
```

### Health Check
```bash
# Port forward backend
kubectl port-forward svc/todo-chatbot-backend 8000:8000

# Test health endpoint
curl http://localhost:8000/health
```

---

## 🧪 Testing

### Functionality Verification

1. **Authentication**: Create account and login
2. **Task CRUD**: Create, view, update, delete tasks
3. **Chatbot**: Use natural language commands
4. **Persistence**: Verify data survives pod restart

### Data Persistence Test
```bash
# Note current tasks
# Delete backend pod
kubectl delete pod -l app=todo-backend

# Wait for recreation
kubectl get pods -w

# Verify tasks persist (Neon DB)
```

---

## 🛠️ Troubleshooting

### Pods Not Starting
```bash
# Check events
kubectl get events --sort-by=.lastTimestamp

# Describe pod
kubectl describe pod -l app=todo-backend
```

### Image Pull Issues
```bash
# Verify images in Minikube
minikube image ls | grep todo

# If missing, rebuild with Minikube Docker
eval $(minikube docker-env)
docker build -t todo-backend:latest -f docker/Dockerfile.backend .
```

### Secret Issues
```bash
# Verify secret exists
kubectl get secrets todo-chatbot-secrets

# View secret keys
kubectl describe secret todo-chatbot-secrets
```

---

## 🧹 Cleanup

```bash
# Uninstall Helm release
helm uninstall todo-chatbot

# Delete secrets
kubectl delete secret todo-chatbot-secrets

# Stop Minikube
minikube stop

# Delete cluster (optional)
minikube delete
```

---

## 📈 Success Criteria

| Metric | Target | Status |
|--------|--------|--------|
| Image build time | <5 min each | ✅ |
| Combined image size | <300MB | ✅ |
| helm lint | 0 errors | ✅ |
| Pod startup time | <2 min | ✅ |
| UI load time | <10 sec | ✅ |
| Full deployment | <15 min | ✅ |

---

## 🔗 Related Documentation

- [Spec](specs/004-local-k8s-deployment/spec.md) - Feature specification
- [Plan](specs/004-local-k8s-deployment/plan.md) - Implementation plan
- [Tasks](specs/004-local-k8s-deployment/tasks.md) - Task breakdown

---

## 📝 Multi-Agent Orchestration

This deployment was orchestrated using a multi-agent workflow:

```
BlueprintAgent (Orchestration)
    ↓
DockerAgent (Image Build)
    ↓
HelmAgent (Chart Creation)
    ↓
K8sAgent (Deployment)
```

Each agent specialized in its domain:
- **BlueprintAgent**: Overall workflow coordination, documentation
- **DockerAgent**: Dockerfile optimization with Gordon AI
- **HelmAgent**: Helm chart creation with kubectl-ai
- **K8sAgent**: Minikube deployment with kagent

---

*Phase IV - Local Kubernetes Deployment Complete*
*Version 1.0.0*
