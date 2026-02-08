# Todo Chatbot Helm Chart

## Overview

Helm chart for deploying the AI-powered Todo Chatbot with Dapr sidecar injection and Kafka (Redpanda) event streaming on Kubernetes.

**Chart Version**: 2.0.0
**App Version**: 5.0.0-partb

## Prerequisites

- Kubernetes 1.28+
- Helm 3.x
- Dapr 1.12+ (for Dapr features)
- Docker images built locally (for Minikube)

## Quick Start

```bash
# Without Dapr (Phase IV compatible)
helm install todo-chatbot ./helm/todo-chatbot

# With Dapr + Kafka (Phase V Part B)
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values-dapr.yaml \
  --set secrets.databaseUrl="YOUR_DATABASE_URL" \
  --set secrets.cohereApiKey="YOUR_COHERE_API_KEY" \
  --set secrets.jwtSecret="YOUR_JWT_SECRET"
```

## Values Reference

### Global Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `nameOverride` | string | `""` | Override chart name |
| `fullnameOverride` | string | `""` | Override full name |

### Backend Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `backend.name` | string | `"todo-backend"` | Container name |
| `backend.replicaCount` | int | `1` | Number of replicas |
| `backend.image.repository` | string | `"todo-backend"` | Docker image |
| `backend.image.tag` | string | `"latest"` | Image tag |
| `backend.image.pullPolicy` | string | `"IfNotPresent"` | Pull policy |
| `backend.dapr.enabled` | bool | `false` | Enable Dapr sidecar |
| `backend.dapr.appId` | string | `"todo-backend"` | Dapr app ID |
| `backend.dapr.appPort` | string | `"8000"` | App port for Dapr |
| `backend.service.type` | string | `"ClusterIP"` | Service type |
| `backend.service.port` | int | `8000` | Service port |
| `backend.resources.limits.cpu` | string | `"500m"` | CPU limit |
| `backend.resources.limits.memory` | string | `"512Mi"` | Memory limit |
| `backend.resources.requests.cpu` | string | `"100m"` | CPU request |
| `backend.resources.requests.memory` | string | `"256Mi"` | Memory request |
| `backend.healthcheck.path` | string | `"/health"` | Health check path |
| `backend.healthcheck.port` | int | `8000` | Health check port |
| `backend.env.HOST` | string | `"0.0.0.0"` | Listen host |
| `backend.env.PORT` | string | `"8000"` | Listen port |
| `backend.env.DEBUG` | string | `"False"` | Debug mode |
| `backend.env.CORS_ORIGINS` | string | `"http://localhost:3000"` | CORS origins |

### Frontend Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `frontend.name` | string | `"todo-frontend"` | Container name |
| `frontend.replicaCount` | int | `1` | Number of replicas |
| `frontend.image.repository` | string | `"todo-frontend"` | Docker image |
| `frontend.image.tag` | string | `"latest"` | Image tag |
| `frontend.image.pullPolicy` | string | `"IfNotPresent"` | Pull policy |
| `frontend.dapr.enabled` | bool | `false` | Enable Dapr sidecar |
| `frontend.dapr.appId` | string | `"todo-frontend"` | Dapr app ID |
| `frontend.dapr.appPort` | string | `"3000"` | App port for Dapr |
| `frontend.service.type` | string | `"NodePort"` | Service type |
| `frontend.service.port` | int | `3000` | Service port |
| `frontend.service.nodePort` | int | `30000` | NodePort number |
| `frontend.resources.limits.cpu` | string | `"500m"` | CPU limit |
| `frontend.resources.limits.memory` | string | `"512Mi"` | Memory limit |
| `frontend.env.NODE_ENV` | string | `"production"` | Node environment |

### Dapr Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `dapr.enabled` | bool | `false` | Enable Dapr globally |
| `dapr.logLevel` | string | `"info"` | Dapr sidecar log level |

### Kafka/Redpanda Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `kafka.enabled` | bool | `false` | Enable Kafka deployment |
| `kafka.broker` | string | `"redpanda"` | Broker type |
| `redpanda.image.repository` | string | `"docker.redpanda.com/redpandadata/redpanda"` | Redpanda image |
| `redpanda.image.tag` | string | `"v23.3.5"` | Redpanda version |
| `redpanda.resources.limits.memory` | string | `"1Gi"` | Memory limit |
| `redpanda.resources.limits.cpu` | string | `"1"` | CPU limit |
| `redpanda.resources.requests.memory` | string | `"256Mi"` | Memory request |
| `redpanda.resources.requests.cpu` | string | `"200m"` | CPU request |

### Secrets Configuration

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `secrets.databaseUrl` | string | `""` | PostgreSQL connection string |
| `secrets.cohereApiKey` | string | `""` | Cohere API key |
| `secrets.jwtSecret` | string | `""` | JWT signing secret |

### ConfigMap Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `config.jwtAlgorithm` | string | `"HS256"` | JWT algorithm |
| `config.jwtExpirationDays` | string | `"7"` | JWT token TTL |

## Values Files

| File | Purpose |
|------|---------|
| `values.yaml` | Default values (Dapr/Kafka disabled) |
| `values-dapr.yaml` | Phase V Part B with Dapr + Kafka enabled |
| `values-local.yaml` | Local development overrides |

## Dapr Components

When `dapr.enabled=true`, the following Dapr components are deployed:

| Component | Type | Purpose |
|-----------|------|---------|
| `kafka-pubsub` | `pubsub.kafka` | Event publishing to Redpanda |
| `statestore` | `state.postgresql` | Dapr state management via Neon PostgreSQL |
| `kubernetes-secrets` | `secretstores.kubernetes` | K8s native secret access |

## Templates

| Template | Description |
|----------|-------------|
| `backend-deployment.yaml` | FastAPI backend with optional Dapr sidecar |
| `frontend-deployment.yaml` | Next.js frontend with optional Dapr sidecar |
| `backend-service.yaml` | ClusterIP service for backend |
| `frontend-service.yaml` | NodePort service for frontend |
| `configmap.yaml` | Application configuration |
| `secret.yaml` | Kubernetes secrets (base64 encoded) |
| `dapr/pubsub-kafka.yaml` | Dapr Kafka pub/sub component |
| `dapr/statestore.yaml` | Dapr PostgreSQL state store |
| `dapr/secretstore.yaml` | Dapr Kubernetes secret store |
| `kafka/redpanda-deployment.yaml` | Redpanda broker deployment |
| `kafka/redpanda-service.yaml` | Redpanda service (9092, 8081, 8082, 9644) |

## Uninstall

```bash
helm uninstall todo-chatbot
```
