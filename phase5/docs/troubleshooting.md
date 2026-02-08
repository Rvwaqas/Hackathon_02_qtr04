# Troubleshooting Guide - Phase V Part B

## Common Issues

### 1. Pods stuck in Pending/CrashLoopBackOff

**Check events:**
```bash
kubectl get events --sort-by=.lastTimestamp
kubectl describe pod <pod-name>
```

**Common causes:**
- Insufficient resources: Increase Minikube memory (`minikube start --memory=6144`)
- Image pull error: Ensure `imagePullPolicy: Never` and images built in Minikube's Docker
- Missing secrets: Create secrets before deployment

### 2. Dapr sidecar not injecting (1/1 instead of 2/2)

**Check:**
```bash
dapr status -k
kubectl get pods -n dapr-system
```

**Fix:**
- Ensure Dapr is installed: `dapr init -k --wait`
- Check annotations: `kubectl get deploy todo-chatbot-backend -o yaml | grep dapr`
- Restart pods: `kubectl rollout restart deployment/todo-chatbot-backend`

### 3. Dapr component not loading

**Check sidecar logs:**
```bash
kubectl logs -l app=todo-backend -c daprd --tail=50
```

**Common errors:**
- `ERR_PUBSUB_NOT_CONFIGURED`: kafka-pubsub component missing or broker unreachable
- `ERR_STATE_STORE_NOT_CONFIGURED`: statestore component missing or DB unreachable

### 4. Redpanda/Kafka not accessible

**Check pod:**
```bash
kubectl get pods -l app=redpanda
kubectl logs -l app=redpanda --tail=30
```

**Test connectivity:**
```bash
kubectl exec deployment/redpanda -- rpk cluster info --brokers localhost:9092
```

### 5. Pub/Sub publish failing

**Test manually:**
```bash
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -v -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
  -H "Content-Type: application/json" \
  -d '{"test":"message"}'
```

**Expected:** HTTP 204 (success) or HTTP 200

### 6. State store connection error

**Check database URL:**
```bash
kubectl get secret todo-chatbot-secrets -o jsonpath='{.data.database-url}' | base64 -d
```

### 7. Secrets not accessible via Dapr

**Test:**
```bash
kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \
  curl -s http://localhost:3500/v1.0/secrets/kubernetes-secrets/todo-chatbot-secrets
```

**Fix:** Ensure the secret exists in the same namespace.

## Debug Commands

```bash
# Full pod details
kubectl describe pods

# Dapr system health
dapr status -k

# Sidecar logs
kubectl logs <pod-name> -c daprd

# Application logs
kubectl logs <pod-name> -c todo-backend

# Events timeline
kubectl get events --sort-by=.lastTimestamp

# Resource usage
kubectl top pods
kubectl top nodes
```

## Recovery Steps

### Full redeployment
```bash
helm uninstall todo-chatbot
kubectl delete components.dapr.io --all
helm upgrade --install todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-dapr.yaml --wait
```

### Restart Dapr
```bash
dapr uninstall -k
dapr init -k --wait
kubectl rollout restart deployment --all
```
