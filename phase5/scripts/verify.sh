#!/bin/bash
# Phase IV - Verification Script
# Verifies the deployment is working correctly

set -e

echo "============================================="
echo "  Phase IV - Deployment Verification"
echo "============================================="

# Check pods status
echo ""
echo "[1/4] Checking pod status..."
kubectl get pods -l "app.kubernetes.io/instance=todo-chatbot"

# Check if all pods are running
BACKEND_READY=$(kubectl get pods -l app=todo-backend -o jsonpath='{.items[0].status.containerStatuses[0].ready}' 2>/dev/null || echo "false")
FRONTEND_READY=$(kubectl get pods -l app=todo-frontend -o jsonpath='{.items[0].status.containerStatuses[0].ready}' 2>/dev/null || echo "false")

if [ "$BACKEND_READY" != "true" ] || [ "$FRONTEND_READY" != "true" ]; then
    echo "Warning: Not all pods are ready"
    echo "Backend ready: $BACKEND_READY"
    echo "Frontend ready: $FRONTEND_READY"
fi

# Check services
echo ""
echo "[2/4] Checking services..."
kubectl get services -l "app.kubernetes.io/instance=todo-chatbot"

# Test backend health
echo ""
echo "[3/4] Testing backend health endpoint..."
kubectl port-forward svc/todo-chatbot-backend 8000:8000 &
PF_PID=$!
sleep 3

if curl -s http://localhost:8000/health | grep -q "ok\|healthy\|status"; then
    echo "Backend health check: PASSED"
else
    echo "Backend health check: FAILED or no health endpoint"
fi

kill $PF_PID 2>/dev/null || true

# Get frontend URL
echo ""
echo "[4/4] Getting frontend URL..."
FRONTEND_URL=$(minikube service todo-chatbot-frontend --url 2>/dev/null || echo "Unable to get URL")
echo "Frontend URL: $FRONTEND_URL"

echo ""
echo "============================================="
echo "  Verification Summary"
echo "============================================="
echo "Backend Pod: $BACKEND_READY"
echo "Frontend Pod: $FRONTEND_READY"
echo "Frontend URL: $FRONTEND_URL"
echo ""
echo "Manual verification steps:"
echo "1. Open $FRONTEND_URL in your browser"
echo "2. Create a new user account"
echo "3. Login and create a task"
echo "4. Use the chatbot to add a task"
