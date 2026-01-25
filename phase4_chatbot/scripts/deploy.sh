#!/bin/bash
# Phase IV - AI-Powered Todo Chatbot Deployment Script
# This script deploys the application to Minikube using Helm

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "============================================="
echo "  Phase IV - Todo Chatbot Deployment"
echo "============================================="

# Check prerequisites
echo ""
echo "[1/7] Checking prerequisites..."
command -v docker >/dev/null 2>&1 || { echo "Error: Docker is required"; exit 1; }
command -v minikube >/dev/null 2>&1 || { echo "Error: Minikube is required"; exit 1; }
command -v kubectl >/dev/null 2>&1 || { echo "Error: kubectl is required"; exit 1; }
command -v helm >/dev/null 2>&1 || { echo "Error: Helm is required"; exit 1; }
echo "All prerequisites met."

# Check if minikube is running
echo ""
echo "[2/7] Checking Minikube status..."
if ! minikube status | grep -q "Running"; then
    echo "Starting Minikube..."
    minikube start --cpus=4 --memory=8192 --driver=docker
fi
echo "Minikube is running."

# Configure Docker to use Minikube's Docker daemon
echo ""
echo "[3/7] Configuring Docker for Minikube..."
eval $(minikube docker-env)

# Build Docker images
echo ""
echo "[4/7] Building Docker images..."
echo "Building backend image..."
docker build -t todo-backend:latest -f "$PROJECT_DIR/docker/Dockerfile.backend" "$PROJECT_DIR"
echo "Building frontend image..."
docker build -t todo-frontend:latest -f "$PROJECT_DIR/docker/Dockerfile.frontend" "$PROJECT_DIR"

# Verify images
echo ""
echo "[5/7] Verifying images..."
echo "Images built:"
docker images | grep -E "^todo-(frontend|backend)"

# Create secrets (if not exists)
echo ""
echo "[6/7] Creating Kubernetes secrets..."
if ! kubectl get secret todo-chatbot-secrets >/dev/null 2>&1; then
    echo "Please provide the following values:"
    read -p "DATABASE_URL: " DATABASE_URL
    read -p "COHERE_API_KEY: " COHERE_API_KEY
    read -p "JWT_SECRET: " JWT_SECRET

    kubectl create secret generic todo-chatbot-secrets \
        --from-literal=database-url="$DATABASE_URL" \
        --from-literal=cohere-api-key="$COHERE_API_KEY" \
        --from-literal=jwt-secret="$JWT_SECRET"
    echo "Secrets created."
else
    echo "Secrets already exist."
fi

# Deploy with Helm
echo ""
echo "[7/7] Deploying with Helm..."
cd "$PROJECT_DIR"

if helm list | grep -q "todo-chatbot"; then
    echo "Upgrading existing deployment..."
    helm upgrade todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-local.yaml
else
    echo "Installing new deployment..."
    helm install todo-chatbot ./helm/todo-chatbot -f ./helm/todo-chatbot/values-local.yaml
fi

# Wait for pods to be ready
echo ""
echo "Waiting for pods to be ready..."
kubectl wait --for=condition=ready pod -l app=todo-backend --timeout=120s
kubectl wait --for=condition=ready pod -l app=todo-frontend --timeout=120s

# Show status
echo ""
echo "============================================="
echo "  Deployment Complete!"
echo "============================================="
kubectl get pods
echo ""
echo "To access the application:"
echo "  minikube service todo-chatbot-frontend --url"
echo ""
echo "To view logs:"
echo "  kubectl logs -l app=todo-backend"
echo "  kubectl logs -l app=todo-frontend"
