# Phase V Part B - Local Minikube + Dapr + Kafka Deployment

## Architecture

```
MINIKUBE CLUSTER
├── dapr-system namespace
│   ├── dapr-operator
│   ├── dapr-sidecar-injector
│   ├── dapr-placement-server
│   └── dapr-sentry
│
├── default namespace
│   ├── todo-backend (FastAPI + Dapr sidecar)    [2/2 containers]
│   ├── todo-frontend (Next.js + Dapr sidecar)   [2/2 containers]
│   ├── redpanda (Kafka broker)                  [1/1 container]
│   │
│   └── Dapr Components:
│       ├── kafka-pubsub (pubsub.kafka)
│       ├── statestore (state.postgresql)
│       └── kubernetes-secrets (secretstores.kubernetes)
│
└── External: Neon PostgreSQL
```

## Prerequisites

| Tool | Version | Check Command |
|------|---------|---------------|
| Docker Desktop | Running | `docker info` |
| Minikube | v1.30+ | `minikube version` |
| kubectl | Latest | `kubectl version --client` |
| Helm | 3.x | `helm version` |
| Dapr CLI | v1.12+ | `dapr --version` |

## Quick Start

### 1. Start Minikube Cluster

```bash
minikube start --memory=4096 --cpus=2 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Install Dapr Runtime

```bash
dapr init -k --wait
dapr status -k
```

Verify all components are healthy:
```
NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS
dapr-operator          dapr-system  True     Running  1
dapr-sidecar-injector  dapr-system  True     Running  1
dapr-placement-server  dapr-system  True     Running  1
dapr-sentry            dapr-system  True     Running  1
```

### 3. Build Docker Images

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build images (context is phase5/)
docker build -t todo-backend:latest -f docker/Dockerfile.backend .
docker build -t todo-frontend:latest -f docker/Dockerfile.frontend .

# Verify images are available
docker images | grep todo-
```

### 4. Create Kubernetes Secrets

```bash
kubectl create secret generic todo-chatbot-secrets \
  --from-literal=database-url="YOUR_NEON_DATABASE_URL" \
  --from-literal=cohere-api-key="YOUR_COHERE_API_KEY" \
  --from-literal=jwt-secret="YOUR_JWT_SECRET"
```

### 5. Deploy with Helm

```bash
helm upgrade --install todo-chatbot helm/todo-chatbot \
  -f helm/todo-chatbot/values-dapr.yaml \
  --wait --timeout 5m
```

### 6. Verify Deployment

```bash
# Check pods (app pods should show 2/2 for Dapr sidecar)
kubectl get pods

# Expected output:
# NAME                                    READY   STATUS    RESTARTS   AGE
# todo-chatbot-backend-xxx                2/2     Running   0          ...
# todo-chatbot-frontend-xxx               2/2     Running   0          ...
# redpanda-xxx                            1/1     Running   0          ...

# Check Dapr components
kubectl get components.dapr.io

# Check services
kubectl get svc

# Access frontend
minikube service todo-chatbot-frontend --url
```

## Verification Commands

### Test Pub/Sub (Kafka)

```bash
# Publish a test event via Dapr sidecar
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"specversion":"1.0","type":"com.todo.task.test","source":"/test","id":"test-1","data":{"test":true}}'

# Expected: empty response (HTTP 204 = success)

# Consume from Kafka to verify
kubectl exec deployment/redpanda -- rpk topic consume task-events -n 1 --brokers localhost:9092
```

### Test State Store

```bash
# Save state
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s -X POST http://localhost:3500/v1.0/state/statestore \
  -H "Content-Type: application/json" \
  -d '[{"key":"test-key","value":{"message":"hello dapr"}}]'

# Get state
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s http://localhost:3500/v1.0/state/statestore/test-key
# Expected: {"message":"hello dapr"}
```

### Test Secrets

```bash
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s http://localhost:3500/v1.0/secrets/kubernetes-secrets/todo-chatbot-secrets
```

### Test Service Invocation

```bash
kubectl exec deployment/todo-chatbot-frontend -c todo-frontend -- \
  curl -s http://localhost:3500/v1.0/invoke/todo-backend/method/health
```

### Test Jobs API

```bash
# Schedule a job
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s -X POST http://localhost:3500/v1.0/jobs/test-job \
  -H "Content-Type: application/json" \
  -d '{"schedule":"@every 1m","data":{"test":"job"}}'

# Delete job
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s -X DELETE http://localhost:3500/v1.0/jobs/test-job
```

## Dapr Building Blocks Summary

| # | Building Block | Component | Test |
|---|----------------|-----------|------|
| 1 | Pub/Sub | kafka-pubsub | Publish event, verify in Kafka |
| 2 | State Store | statestore | Save/retrieve state |
| 3 | Secrets | kubernetes-secrets | Get API key via Dapr |
| 4 | Jobs | Built-in | Schedule/delete job |
| 5 | Service Invocation | Built-in | Cross-service health check |

## Kafka Topics

| Topic | Events |
|-------|--------|
| task-events | task.created, task.updated, task.completed, task.deleted |
| reminders | reminder.due, recurring.triggered |

## Helm Values Files

| File | Purpose |
|------|---------|
| `values.yaml` | Base defaults (Dapr/Kafka disabled) |
| `values-dapr.yaml` | Phase V Part B (Dapr + Kafka enabled) |
| `values-local.yaml` | Local dev overrides (pullPolicy: Never) |

## Alternative: Docker Compose (without Dapr)

For local testing without Kubernetes/Dapr:

```bash
cd phase5
cp .env.example .env  # Fill in your values
docker compose up --build
```

Note: Docker Compose runs the app without Dapr sidecars. Event publishing will gracefully degrade (logged but not sent to Kafka).

## Cleanup

```bash
helm uninstall todo-chatbot
dapr uninstall -k
minikube stop
minikube delete
```

## Further Reading

- [Dapr Components Reference](docs/dapr-components.md)
- [Troubleshooting Guide](docs/troubleshooting.md)
- [Helm Chart README](helm/todo-chatbot/README.md)
- [Specification](specs/006-phase5-partb-local-deployment/spec.md)
