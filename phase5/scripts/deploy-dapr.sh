#!/bin/bash
# Phase V Part B - Full Deployment Script
# Deploys Todo Chatbot with Dapr + Kafka on Minikube
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PHASE5_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
HELM_DIR="$PHASE5_DIR/helm/todo-chatbot"

echo "=========================================="
echo " Phase V Part B - Dapr + Kafka Deployment"
echo "=========================================="

# Step 1: Verify prerequisites
echo ""
echo "[1/8] Checking prerequisites..."
command -v minikube >/dev/null 2>&1 || { echo "ERROR: minikube not installed"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "ERROR: kubectl not installed"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "ERROR: helm not installed"; exit 1; }
command -v dapr >/dev/null 2>&1 || { echo "ERROR: dapr CLI not installed"; exit 1; }
echo "  All prerequisites found."

# Step 2: Start Minikube if not running
echo ""
echo "[2/8] Checking Minikube cluster..."
if minikube status | grep -q "Running" 2>/dev/null; then
    echo "  Minikube is already running."
else
    echo "  Starting Minikube..."
    minikube start --memory=4096 --cpus=2 --driver=docker
fi

# Step 3: Enable addons
echo ""
echo "[3/8] Enabling Minikube addons..."
minikube addons enable ingress 2>/dev/null || true
minikube addons enable metrics-server 2>/dev/null || true
echo "  Addons enabled."

# Step 4: Install Dapr
echo ""
echo "[4/8] Installing Dapr on cluster..."
if dapr status -k 2>/dev/null | grep -q "Running"; then
    echo "  Dapr is already installed."
else
    echo "  Installing Dapr..."
    dapr init -k --wait
fi
echo "  Dapr status:"
dapr status -k

# Step 5: Build Docker images
echo ""
echo "[5/8] Building Docker images..."
eval $(minikube docker-env)
echo "  Building backend..."
docker build -t todo-backend:latest -f "$PHASE5_DIR/docker/Dockerfile.backend" "$PHASE5_DIR"
echo "  Building frontend..."
docker build -t todo-frontend:latest -f "$PHASE5_DIR/docker/Dockerfile.frontend" "$PHASE5_DIR"
echo "  Images built."

# Step 6: Create secrets (if not exist)
echo ""
echo "[6/8] Checking secrets..."
if ! kubectl get secret todo-chatbot-secrets >/dev/null 2>&1; then
    echo "  WARNING: Secrets not found. Create them with:"
    echo "  kubectl create secret generic todo-chatbot-secrets \\"
    echo "    --from-literal=database-url=YOUR_DATABASE_URL \\"
    echo "    --from-literal=cohere-api-key=YOUR_COHERE_API_KEY \\"
    echo "    --from-literal=jwt-secret=YOUR_JWT_SECRET"
    echo ""
    echo "  Skipping secret creation (user must provide values)."
else
    echo "  Secrets already exist."
fi

# Step 7: Deploy with Helm
echo ""
echo "[7/8] Deploying with Helm..."
helm upgrade --install todo-chatbot "$HELM_DIR" \
    -f "$HELM_DIR/values-dapr.yaml" \
    --wait --timeout 5m
echo "  Helm deployment complete."

# Step 8: Verify deployment
echo ""
echo "[8/8] Verifying deployment..."
echo ""
echo "--- Pods ---"
kubectl get pods
echo ""
echo "--- Services ---"
kubectl get svc
echo ""
echo "--- Dapr Components ---"
kubectl get components.dapr.io 2>/dev/null || echo "  (No Dapr components yet)"
echo ""
echo "=========================================="
echo " Deployment Complete!"
echo "=========================================="
echo ""
echo "Access frontend:"
echo "  minikube service todo-chatbot-frontend --url"
echo ""
echo "Test Kafka event publishing:"
echo "  kubectl exec deployment/todo-chatbot-backend -c todo-backend -- \\"
echo "    curl -s -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \\"
echo "    -H 'Content-Type: application/json' \\"
echo "    -d '{\"specversion\":\"1.0\",\"type\":\"com.todo.task.test\",\"source\":\"/test\",\"id\":\"test-1\",\"data\":{\"test\":true}}'"
echo ""
echo "Consume from Kafka:"
echo "  kubectl exec deployment/redpanda -- rpk topic consume task-events -n 1 --brokers localhost:9092"
