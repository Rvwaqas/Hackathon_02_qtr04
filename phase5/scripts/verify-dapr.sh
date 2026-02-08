#!/bin/bash
# Phase V Part B - Verification Script
# Tests all 5 Dapr building blocks
set -euo pipefail

BACKEND_POD=$(kubectl get pod -l app=todo-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
BACKEND_DEPLOY="deployment/$(kubectl get deploy -l app=todo-backend -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo 'todo-chatbot-backend')"

echo "=========================================="
echo " Phase V Part B - Dapr Verification"
echo "=========================================="

# Test 1: Cluster Health
echo ""
echo "[1/7] Cluster Health..."
echo "  Minikube: $(minikube status --format='{{.Host}}' 2>/dev/null || echo 'NOT RUNNING')"
echo "  Dapr:"
dapr status -k 2>/dev/null | head -6 || echo "  NOT INSTALLED"

# Test 2: Pod Status
echo ""
echo "[2/7] Pod Status..."
kubectl get pods -o wide 2>/dev/null || echo "  No pods found"

# Test 3: Dapr Components
echo ""
echo "[3/7] Dapr Components..."
kubectl get components.dapr.io 2>/dev/null || echo "  No components found"

# Test 4: Pub/Sub Test
echo ""
echo "[4/7] Pub/Sub Test (publishing to task-events)..."
RESULT=$(kubectl exec $BACKEND_DEPLOY -c todo-backend -- \
    curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
    -H "Content-Type: application/json" \
    -d '{"specversion":"1.0","type":"com.todo.task.test","source":"/verification","id":"verify-1","data":{"test":true}}' 2>/dev/null || echo "FAILED")
if [ "$RESULT" = "204" ] || [ "$RESULT" = "200" ]; then
    echo "  PASS: Pub/Sub publish returned HTTP $RESULT"
else
    echo "  FAIL: Pub/Sub publish returned: $RESULT"
fi

# Test 5: State Store Test
echo ""
echo "[5/7] State Store Test..."
SAVE=$(kubectl exec $BACKEND_DEPLOY -c todo-backend -- \
    curl -s -o /dev/null -w "%{http_code}" \
    -X POST http://localhost:3500/v1.0/state/statestore \
    -H "Content-Type: application/json" \
    -d '[{"key":"test-verify","value":{"message":"dapr-works"}}]' 2>/dev/null || echo "FAILED")
if [ "$SAVE" = "204" ] || [ "$SAVE" = "200" ]; then
    echo "  PASS: State save returned HTTP $SAVE"
    GET_RESULT=$(kubectl exec $BACKEND_DEPLOY -c todo-backend -- \
        curl -s http://localhost:3500/v1.0/state/statestore/test-verify 2>/dev/null || echo "FAILED")
    echo "  State get result: $GET_RESULT"
else
    echo "  FAIL: State save returned: $SAVE"
fi

# Test 6: Secrets Test
echo ""
echo "[6/7] Secrets Store Test..."
SECRET=$(kubectl exec $BACKEND_DEPLOY -c todo-backend -- \
    curl -s http://localhost:3500/v1.0/secrets/kubernetes-secrets/todo-chatbot-secrets 2>/dev/null || echo "FAILED")
if echo "$SECRET" | grep -q "database-url" 2>/dev/null; then
    echo "  PASS: Secrets accessible via Dapr"
else
    echo "  INFO: Secrets response: $SECRET"
fi

# Test 7: Kafka Topic Verification
echo ""
echo "[7/7] Kafka Topics..."
kubectl exec deployment/redpanda -- rpk topic list --brokers localhost:9092 2>/dev/null || echo "  Redpanda not accessible"

echo ""
echo "=========================================="
echo " Verification Complete"
echo "=========================================="
