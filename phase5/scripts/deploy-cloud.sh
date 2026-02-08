#!/bin/bash
# Phase V Part C - Cloud Deploy Script (Linux/Mac)
# Deploy Todo Chatbot to Oracle OKE with Dapr + Redpanda Cloud
#
# Prerequisites:
#   - OCI CLI configured (oci setup config)
#   - kubectl connected to OKE cluster
#   - Dapr installed on cluster (dapr init -k --wait)
#   - Docker images pushed to ghcr.io
#   - K8s secrets created (todo-secrets, kafka-secrets)
#
# Usage:
#   ./scripts/deploy-cloud.sh \
#     --broker-url "<REDPANDA_BOOTSTRAP_URL>:9092" \
#     --database-url "<NEON_URL>" \
#     --cohere-key "<COHERE_API_KEY>" \
#     --jwt-secret "<JWT_SECRET>"

set -euo pipefail

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[DEPLOY]${NC} $1"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# Parse arguments
BROKER_URL=""
DATABASE_URL=""
COHERE_KEY=""
JWT_SECRET=""
IMAGE_TAG="latest"

while [[ $# -gt 0 ]]; do
  case $1 in
    --broker-url) BROKER_URL="$2"; shift 2 ;;
    --database-url) DATABASE_URL="$2"; shift 2 ;;
    --cohere-key) COHERE_KEY="$2"; shift 2 ;;
    --jwt-secret) JWT_SECRET="$2"; shift 2 ;;
    --image-tag) IMAGE_TAG="$2"; shift 2 ;;
    *) error "Unknown argument: $1" ;;
  esac
done

# Validate required arguments
[[ -z "$BROKER_URL" ]] && error "Missing --broker-url"
[[ -z "$DATABASE_URL" ]] && error "Missing --database-url"
[[ -z "$COHERE_KEY" ]] && error "Missing --cohere-key"
[[ -z "$JWT_SECRET" ]] && error "Missing --jwt-secret"

# Determine script directory and helm chart path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHASE5_DIR="$(dirname "$SCRIPT_DIR")"
CHART_DIR="$PHASE5_DIR/helm/todo-chatbot"

log "Phase V Part C - Cloud Deployment to Oracle OKE"
log "================================================"

# Step 1: Verify kubectl connectivity
log "Step 1: Verifying kubectl connectivity..."
kubectl get nodes || error "Cannot connect to cluster. Run: oci ce cluster create-kubeconfig ..."
echo ""

# Step 2: Verify Dapr
log "Step 2: Verifying Dapr installation..."
dapr status -k || error "Dapr not installed. Run: dapr init -k --wait"
echo ""

# Step 3: Deploy with Helm
log "Step 3: Deploying with Helm (cloud values)..."
helm upgrade --install todo-chatbot "$CHART_DIR" \
  -f "$CHART_DIR/values.yaml" \
  -f "$CHART_DIR/values-cloud.yaml" \
  --set backend.image.tag="$IMAGE_TAG" \
  --set frontend.image.tag="$IMAGE_TAG" \
  --set kafka.brokerUrl="$BROKER_URL" \
  --set secrets.databaseUrl="$DATABASE_URL" \
  --set secrets.cohereApiKey="$COHERE_KEY" \
  --set secrets.jwtSecret="$JWT_SECRET" \
  --wait --timeout 300s

echo ""
log "Step 4: Verifying deployment..."
kubectl get pods
echo ""
kubectl get svc
echo ""

# Step 5: Wait for LoadBalancer
log "Step 5: Waiting for LoadBalancer external IP..."
echo "Run: kubectl get svc -w"
echo "Look for EXTERNAL-IP on the frontend service."
echo ""

EXTERNAL_IP=$(kubectl get svc todo-chatbot-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo "pending")
if [[ "$EXTERNAL_IP" != "pending" && -n "$EXTERNAL_IP" ]]; then
  log "Frontend accessible at: http://$EXTERNAL_IP:3000"
else
  warn "LoadBalancer IP not yet assigned. Run: kubectl get svc -w"
fi

log "Deployment complete!"
