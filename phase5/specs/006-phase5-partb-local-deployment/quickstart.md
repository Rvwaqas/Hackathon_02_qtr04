# Quickstart: Phase V Part B - Local Minikube + Dapr + Kafka

**Feature ID**: 006-phase5-partb-local-deployment
**Created**: 2026-02-04

---

## Prerequisites

Before starting, ensure you have:

- [ ] Docker Desktop running
- [ ] Minikube installed (v1.30+)
- [ ] kubectl installed and configured
- [ ] Helm 3 installed
- [ ] Dapr CLI installed (v1.12+)
- [ ] Phase V Part A code complete

---

## Quick Deploy (10 Commands)

### 1. Start Minikube

```bash
minikube start --memory=4096 --cpus=2 --driver=docker
minikube addons enable ingress
minikube addons enable metrics-server
```

### 2. Install Dapr

```bash
dapr init -k --wait
dapr status -k  # Verify all healthy
```

### 3. Build and Load Images

```bash
# From phase5 directory
eval $(minikube docker-env)
docker build -t todo-backend:latest ./backend
docker build -t todo-frontend:latest ./frontend
```

### 4. Create Secrets

```bash
kubectl create secret generic db-secrets \
  --from-literal=connection-string="YOUR_NEON_URL"

kubectl create secret generic api-secrets \
  --from-literal=cohere-api-key="YOUR_COHERE_KEY" \
  --from-literal=gemini-api-key="YOUR_GEMINI_KEY" \
  --from-literal=better-auth-secret="YOUR_AUTH_SECRET"
```

### 5. Deploy with Helm

```bash
helm install todo-app ./helm/todo-chatbot -f ./helm/todo-chatbot/values-dapr.yaml
```

### 6. Verify Deployment

```bash
kubectl get pods  # Should show 2/2 containers
kubectl get components.dapr.io  # Should show 3 components
```

### 7. Access Application

```bash
minikube service todo-frontend --url
# Open URL in browser
```

### 8. Verify Events

```bash
# Create a task via chatbot, then:
kubectl exec redpanda-0 -- rpk topic consume task-events -n 1
```

---

## Verification Checklist

| Check | Command | Expected |
|-------|---------|----------|
| Minikube | `minikube status` | Running |
| Dapr | `dapr status -k` | All healthy |
| Pods | `kubectl get pods` | All 2/2, Running |
| Components | `kubectl get components.dapr.io` | 3 components |
| Topics | `kubectl exec redpanda-0 -- rpk topic list` | task-events, reminders |
| App | Open minikube service URL | Login page |

---

## Troubleshooting

### Pods not 2/2?

```bash
# Check if Dapr injector is running
kubectl get pods -n dapr-system

# Restart pods to trigger injection
kubectl rollout restart deployment todo-backend
kubectl rollout restart deployment todo-frontend
```

### Kafka connection issues?

```bash
# Check Redpanda pod
kubectl logs redpanda-0

# Verify service
kubectl get svc redpanda
```

### Events not appearing?

```bash
# Check Dapr sidecar logs
kubectl logs -l app=todo-backend -c daprd

# Test manual publish
kubectl exec -it deployment/todo-backend -c todo-backend -- \
  curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"test": "message"}'
```

---

## Cleanup

```bash
helm uninstall todo-app
kubectl delete secret db-secrets api-secrets
dapr uninstall -k
minikube delete
```
