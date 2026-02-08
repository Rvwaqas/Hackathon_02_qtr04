# Skill: Cloud Kubernetes Deployment

## Purpose
Deploy applications to production-grade cloud Kubernetes clusters. Primary focus on DigitalOcean Kubernetes (DOKS) with support for Azure AKS and Google GKE. Extends Phase IV Helm charts for cloud environments.

## Tech Stack
- **DigitalOcean Kubernetes (DOKS)**: Primary recommendation ($200 free credit)
- **Azure AKS**: Enterprise alternative
- **Google GKE**: GCP alternative
- **Helm**: Chart deployment with cloud value overrides
- **Dapr**: Distributed runtime on cloud K8s
- **Strimzi/Redpanda**: Kafka on cloud clusters

## Cloud Provider Comparison

| Feature | DOKS (Recommended) | AKS | GKE |
|---------|-------------------|-----|-----|
| **Free Credit** | $200 for 60 days | $200 for 30 days | $300 for 90 days |
| **Simplicity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Cost** | ~$12/month (basic) | ~$70/month | ~$70/month |
| **CLI** | doctl | az | gcloud |
| **Load Balancer** | $12/month | Included | Included |
| **Container Registry** | Included | ACR (paid) | GCR (paid) |

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    CLOUD KUBERNETES ARCHITECTURE                         │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                     INTERNET / USERS                              │   │
│  └───────────────────────────┬──────────────────────────────────────┘   │
│                              │                                           │
│                              ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              CLOUD LOAD BALANCER (Public IP)                      │   │
│  │              - DigitalOcean LB / Azure LB / GCP LB               │   │
│  └───────────────────────────┬──────────────────────────────────────┘   │
│                              │                                           │
│  ┌───────────────────────────┼──────────────────────────────────────┐   │
│  │                    KUBERNETES CLUSTER                             │   │
│  │                                                                   │   │
│  │   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │   │   Ingress   │  │   Ingress   │  │   Ingress   │              │   │
│  │   │  /frontend  │  │    /api     │  │   /chat     │              │   │
│  │   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │   │
│  │          │                │                │                      │   │
│  │   ┌──────▼──────┐  ┌──────▼──────┐  ┌──────▼──────┐              │   │
│  │   │  Frontend   │  │   Backend   │  │   Backend   │              │   │
│  │   │  (Next.js)  │  │  (FastAPI)  │  │  (FastAPI)  │              │   │
│  │   │  Replicas:2 │  │  Replicas:2 │  │  Replicas:2 │              │   │
│  │   │  +Dapr      │  │  +Dapr      │  │  +Dapr      │              │   │
│  │   └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                   │   │
│  │   ┌─────────────────────────────────────────────────────────┐    │   │
│  │   │                    DAPR CONTROL PLANE                    │    │   │
│  │   │  - dapr-operator, dapr-sentry, dapr-placement           │    │   │
│  │   └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                   │   │
│  │   ┌─────────────────────────────────────────────────────────┐    │   │
│  │   │                 KAFKA (Strimzi/Redpanda)                 │    │   │
│  │   │  - Brokers: 1-3, Topics: task-events, reminders         │    │   │
│  │   └─────────────────────────────────────────────────────────┘    │   │
│  │                                                                   │   │
│  └───────────────────────────────────────────────────────────────────┘   │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │              MANAGED SERVICES (External)                          │   │
│  │  - Neon PostgreSQL (Database)                                    │   │
│  │  - Redpanda Cloud (Optional managed Kafka)                       │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Part 1: DigitalOcean Kubernetes (DOKS) Setup

### 1.1 Prerequisites

```bash
# ═══════════════════════════════════════════════════════════════
# DIGITALOCEAN SETUP
# ═══════════════════════════════════════════════════════════════

# Step 1: Create DigitalOcean Account
# Go to: https://www.digitalocean.com/
# Sign up with GitHub for $200 free credit (60 days)

# Step 2: Install doctl CLI
# macOS
brew install doctl

# Windows (via scoop)
scoop install doctl

# Linux
wget https://github.com/digitalocean/doctl/releases/download/v1.101.0/doctl-1.101.0-linux-amd64.tar.gz
tar xf doctl-1.101.0-linux-amd64.tar.gz
sudo mv doctl /usr/local/bin

# Step 3: Authenticate doctl
# Get API token from: https://cloud.digitalocean.com/account/api/tokens
doctl auth init
# Paste your API token when prompted

# Verify authentication
doctl account get
```

### 1.2 Create DOKS Cluster

```bash
# ═══════════════════════════════════════════════════════════════
# CREATE KUBERNETES CLUSTER
# ═══════════════════════════════════════════════════════════════

# List available regions
doctl kubernetes options regions

# List available node sizes
doctl kubernetes options sizes

# Create cluster (cost-optimized for hackathon)
doctl kubernetes cluster create todo-cluster \
  --region nyc1 \
  --version 1.29.1-do.0 \
  --node-pool "name=default;size=s-2vcpu-4gb;count=2" \
  --wait

# This creates:
# - 2 nodes with 2 vCPU, 4GB RAM each
# - Estimated cost: ~$24/month (covered by free credit)

# Download kubeconfig and set context
doctl kubernetes cluster kubeconfig save todo-cluster

# Verify connection
kubectl get nodes
# Expected:
# NAME                   STATUS   ROLES    AGE   VERSION
# todo-cluster-default-xxxxx   Ready    <none>   5m    v1.29.1
# todo-cluster-default-yyyyy   Ready    <none>   5m    v1.29.1
```

### 1.3 Configure kubectl Context

```bash
# List all contexts
kubectl config get-contexts

# Switch to DOKS cluster
kubectl config use-context do-nyc1-todo-cluster

# Verify current context
kubectl config current-context
# Output: do-nyc1-todo-cluster

# Create namespaces
kubectl create namespace todo-app
kubectl create namespace kafka
kubectl create namespace dapr-system
```

## Part 2: Helm Value Overrides for Cloud

### 2.1 Cloud Values File Structure

```yaml
# helm/values-doks.yaml
# [Task]: DigitalOcean-specific Helm overrides
# [From]: Phase IV Helm charts extended for cloud

# ═══════════════════════════════════════════════════════════════
# GLOBAL CLOUD SETTINGS
# ═══════════════════════════════════════════════════════════════
global:
  environment: production
  cloudProvider: digitalocean
  region: nyc1

# ═══════════════════════════════════════════════════════════════
# FRONTEND DEPLOYMENT
# ═══════════════════════════════════════════════════════════════
frontend:
  replicaCount: 2  # HA: 2+ replicas

  image:
    repository: registry.digitalocean.com/todo-registry/frontend
    tag: latest
    pullPolicy: Always

  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi

  # Horizontal Pod Autoscaler
  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 5
    targetCPUUtilizationPercentage: 70

  # Service type for cloud
  service:
    type: ClusterIP  # Behind Ingress

  # Dapr sidecar
  dapr:
    enabled: true
    appId: frontend-service
    appPort: 3000

# ═══════════════════════════════════════════════════════════════
# BACKEND DEPLOYMENT
# ═══════════════════════════════════════════════════════════════
backend:
  replicaCount: 2

  image:
    repository: registry.digitalocean.com/todo-registry/backend
    tag: latest
    pullPolicy: Always

  resources:
    requests:
      cpu: 200m
      memory: 256Mi
    limits:
      cpu: 1000m
      memory: 1Gi

  autoscaling:
    enabled: true
    minReplicas: 2
    maxReplicas: 10
    targetCPUUtilizationPercentage: 70

  service:
    type: ClusterIP

  dapr:
    enabled: true
    appId: backend-service
    appPort: 8000

  # Environment variables from secrets
  envFrom:
    - secretRef:
        name: todo-secrets

# ═══════════════════════════════════════════════════════════════
# INGRESS (NGINX)
# ═══════════════════════════════════════════════════════════════
ingress:
  enabled: true
  className: nginx
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"

  hosts:
    - host: todo.yourdomain.com
      paths:
        - path: /
          pathType: Prefix
          service: frontend
        - path: /api
          pathType: Prefix
          service: backend

  tls:
    - secretName: todo-tls
      hosts:
        - todo.yourdomain.com

# ═══════════════════════════════════════════════════════════════
# LOAD BALANCER (DigitalOcean)
# ═══════════════════════════════════════════════════════════════
loadBalancer:
  enabled: true
  annotations:
    service.beta.kubernetes.io/do-loadbalancer-name: "todo-lb"
    service.beta.kubernetes.io/do-loadbalancer-size-slug: "lb-small"
    service.beta.kubernetes.io/do-loadbalancer-protocol: "http"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-path: "/health"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-protocol: "http"
```

### 2.2 Azure AKS Values

```yaml
# helm/values-aks.yaml
# Azure Kubernetes Service overrides

global:
  environment: production
  cloudProvider: azure
  region: eastus

frontend:
  replicaCount: 2
  image:
    repository: todoregistry.azurecr.io/frontend
    tag: latest

backend:
  replicaCount: 2
  image:
    repository: todoregistry.azurecr.io/backend
    tag: latest

ingress:
  enabled: true
  className: azure/application-gateway
  annotations:
    kubernetes.io/ingress.class: azure/application-gateway
    appgw.ingress.kubernetes.io/ssl-redirect: "true"

# Azure-specific load balancer
loadBalancer:
  annotations:
    service.beta.kubernetes.io/azure-load-balancer-internal: "false"
```

### 2.3 Google GKE Values

```yaml
# helm/values-gke.yaml
# Google Kubernetes Engine overrides

global:
  environment: production
  cloudProvider: gcp
  region: us-central1

frontend:
  replicaCount: 2
  image:
    repository: gcr.io/your-project/frontend
    tag: latest

backend:
  replicaCount: 2
  image:
    repository: gcr.io/your-project/backend
    tag: latest

ingress:
  enabled: true
  className: gce
  annotations:
    kubernetes.io/ingress.class: "gce"
    kubernetes.io/ingress.global-static-ip-name: "todo-ip"
```

## Part 3: Load Balancer & External Access

### 3.1 DigitalOcean Load Balancer Service

```yaml
# k8s/loadbalancer-service.yaml
# [Task]: Expose frontend publicly via DO Load Balancer

apiVersion: v1
kind: Service
metadata:
  name: todo-frontend-lb
  namespace: todo-app
  annotations:
    # DigitalOcean Load Balancer configuration
    service.beta.kubernetes.io/do-loadbalancer-name: "todo-frontend-lb"
    service.beta.kubernetes.io/do-loadbalancer-size-slug: "lb-small"
    service.beta.kubernetes.io/do-loadbalancer-protocol: "http"
    service.beta.kubernetes.io/do-loadbalancer-algorithm: "round_robin"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-path: "/"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-protocol: "http"
    service.beta.kubernetes.io/do-loadbalancer-healthcheck-port: "3000"
    # Optional: Enable sticky sessions
    service.beta.kubernetes.io/do-loadbalancer-sticky-sessions-type: "cookies"
    service.beta.kubernetes.io/do-loadbalancer-sticky-sessions-cookie-name: "DO-LB"
    service.beta.kubernetes.io/do-loadbalancer-sticky-sessions-cookie-ttl: "60"
spec:
  type: LoadBalancer
  selector:
    app: frontend
  ports:
    - name: http
      port: 80
      targetPort: 3000
      protocol: TCP
```

### 3.2 Install NGINX Ingress Controller

```bash
# ═══════════════════════════════════════════════════════════════
# NGINX INGRESS CONTROLLER FOR DOKS
# ═══════════════════════════════════════════════════════════════

# Add NGINX Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install NGINX Ingress with DO Load Balancer
helm install nginx-ingress ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/do-loadbalancer-name"="nginx-ingress-lb" \
  --set controller.service.annotations."service\.beta\.kubernetes\.io/do-loadbalancer-size-slug"="lb-small"

# Wait for external IP
kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -w
# Wait until EXTERNAL-IP changes from <pending> to actual IP

# Get the Load Balancer IP
export LB_IP=$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Load Balancer IP: $LB_IP"
```

### 3.3 Ingress Resource

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: todo-ingress
  namespace: todo-app
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/rewrite-target: /
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  ingressClassName: nginx
  rules:
    - http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend
                port:
                  number: 3000
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend
                port:
                  number: 8000
```

## Part 4: Install Dapr on Cloud Cluster

```bash
# ═══════════════════════════════════════════════════════════════
# DAPR INSTALLATION ON CLOUD K8S
# ═══════════════════════════════════════════════════════════════

# Install Dapr CLI (if not already installed)
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Initialize Dapr on the cloud cluster
dapr init -k --wait

# Verify Dapr installation
dapr status -k

# Expected output:
#   NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION
#   dapr-dashboard         dapr-system  True     Running  1         0.14.0
#   dapr-sidecar-injector  dapr-system  True     Running  1         1.13.0
#   dapr-operator          dapr-system  True     Running  1         1.13.0
#   dapr-placement-server  dapr-system  True     Running  1         1.13.0
#   dapr-sentry            dapr-system  True     Running  1         1.13.0

# Apply Dapr components
kubectl apply -f dapr-components/ -n todo-app

# Verify components
dapr components -k -n todo-app
```

## Part 5: Deploy Kafka on Cloud

### Option A: Strimzi (Self-Hosted)

```bash
# ═══════════════════════════════════════════════════════════════
# STRIMZI KAFKA ON CLOUD K8S
# ═══════════════════════════════════════════════════════════════

# Create Kafka namespace
kubectl create namespace kafka

# Install Strimzi operator
kubectl apply -f https://strimzi.io/install/latest?namespace=kafka

# Wait for operator
kubectl wait --for=condition=ready pod -l name=strimzi-cluster-operator -n kafka --timeout=300s
```

```yaml
# kafka/kafka-cloud.yaml
# Production Kafka cluster for cloud
apiVersion: kafka.strimzi.io/v1beta2
kind: Kafka
metadata:
  name: todo-kafka
  namespace: kafka
spec:
  kafka:
    version: 3.6.0
    replicas: 3  # HA: 3 brokers
    listeners:
      - name: plain
        port: 9092
        type: internal
        tls: false
      - name: tls
        port: 9093
        type: internal
        tls: true
    config:
      offsets.topic.replication.factor: 3
      transaction.state.log.replication.factor: 3
      transaction.state.log.min.isr: 2
      default.replication.factor: 3
      min.insync.replicas: 2
      num.partitions: 3
    storage:
      type: persistent-claim
      size: 10Gi
      class: do-block-storage  # DigitalOcean block storage
    resources:
      requests:
        memory: 1Gi
        cpu: 500m
      limits:
        memory: 2Gi
        cpu: 1000m

  zookeeper:
    replicas: 3
    storage:
      type: persistent-claim
      size: 5Gi
      class: do-block-storage
    resources:
      requests:
        memory: 512Mi
        cpu: 250m
      limits:
        memory: 1Gi
        cpu: 500m

  entityOperator:
    topicOperator: {}
    userOperator: {}
```

```bash
# Apply Kafka cluster
kubectl apply -f kafka/kafka-cloud.yaml

# Wait for Kafka (takes a few minutes)
kubectl wait kafka/todo-kafka --for=condition=Ready --timeout=600s -n kafka

# Create topics
kubectl apply -f kafka/kafka-topics.yaml
```

### Option B: Redpanda Cloud (Managed)

```bash
# ═══════════════════════════════════════════════════════════════
# REDPANDA CLOUD (No self-hosting needed)
# ═══════════════════════════════════════════════════════════════

# 1. Go to https://redpanda.com/cloud
# 2. Create Serverless cluster (free tier)
# 3. Create topics in console
# 4. Get connection credentials

# Create secret for Redpanda
kubectl create secret generic kafka-secrets \
  --from-literal=brokers="your-cluster.cloud.redpanda.com:9092" \
  --from-literal=username="your-service-account" \
  --from-literal=password="your-password" \
  -n todo-app
```

## Part 6: Secrets Management

### 6.1 Create Application Secrets

```bash
# ═══════════════════════════════════════════════════════════════
# KUBERNETES SECRETS
# ═══════════════════════════════════════════════════════════════

# Create secrets for the application
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@neon-host/db?sslmode=require" \
  --from-literal=GEMINI_API_KEY="your-gemini-api-key" \
  --from-literal=JWT_SECRET="your-super-secret-jwt-key" \
  --from-literal=COHERE_API_KEY="your-cohere-api-key" \
  -n todo-app

# Verify secrets
kubectl get secrets -n todo-app

# View secret (base64 encoded)
kubectl get secret todo-secrets -n todo-app -o yaml
```

### 6.2 DigitalOcean Spaces for Secrets (Optional)

```bash
# Use DigitalOcean Spaces for encrypted secrets storage
# 1. Create a Space in DO Console
# 2. Store encrypted secrets file
# 3. Use External Secrets Operator to sync

# Install External Secrets Operator
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets \
  --create-namespace
```

## Part 7: Deploy Application

### 7.1 Push Images to Container Registry

```bash
# ═══════════════════════════════════════════════════════════════
# DIGITALOCEAN CONTAINER REGISTRY
# ═══════════════════════════════════════════════════════════════

# Create container registry
doctl registry create todo-registry

# Login to registry
doctl registry login

# Build and push images
cd backend
docker build -t registry.digitalocean.com/todo-registry/backend:latest .
docker push registry.digitalocean.com/todo-registry/backend:latest

cd ../frontend
docker build -t registry.digitalocean.com/todo-registry/frontend:latest .
docker push registry.digitalocean.com/todo-registry/frontend:latest

# Connect registry to cluster
doctl kubernetes cluster registry add todo-cluster
```

### 7.2 Deploy with Helm

```bash
# ═══════════════════════════════════════════════════════════════
# HELM DEPLOYMENT TO CLOUD
# ═══════════════════════════════════════════════════════════════

# Ensure correct context
kubectl config use-context do-nyc1-todo-cluster

# Deploy with cloud values
helm upgrade --install todo-app ./helm/todo-app \
  -f ./helm/values-doks.yaml \
  -n todo-app \
  --create-namespace \
  --wait

# Check deployment status
kubectl get pods -n todo-app
kubectl get svc -n todo-app
kubectl get ingress -n todo-app

# Get external URL
kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller
```

### 7.3 Verification Script

```bash
#!/bin/bash
# verify-deployment.sh

echo "═══════════════════════════════════════════════════════════"
echo "CLOUD DEPLOYMENT VERIFICATION"
echo "═══════════════════════════════════════════════════════════"

echo ""
echo "1. Checking Nodes..."
kubectl get nodes

echo ""
echo "2. Checking Pods..."
kubectl get pods -n todo-app

echo ""
echo "3. Checking Services..."
kubectl get svc -n todo-app

echo ""
echo "4. Checking Ingress..."
kubectl get ingress -n todo-app

echo ""
echo "5. Checking Dapr..."
dapr status -k

echo ""
echo "6. Checking Kafka..."
kubectl get kafka -n kafka

echo ""
echo "7. Getting External URL..."
LB_IP=$(kubectl get svc -n ingress-nginx nginx-ingress-ingress-nginx-controller -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
echo "Application URL: http://$LB_IP"

echo ""
echo "8. Testing Health Endpoints..."
curl -s http://$LB_IP/api/health || echo "Backend health check"
curl -s http://$LB_IP/ | head -20 || echo "Frontend check"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "DEPLOYMENT VERIFICATION COMPLETE"
echo "═══════════════════════════════════════════════════════════"
```

## Part 8: CI/CD with GitHub Actions

```yaml
# .github/workflows/deploy-cloud.yaml
name: Deploy to Cloud K8s

on:
  push:
    branches: [main]
  workflow_dispatch:

env:
  REGISTRY: registry.digitalocean.com/todo-registry
  CLUSTER_NAME: todo-cluster

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install doctl
        uses: digitalocean/action-doctl@v2
        with:
          token: ${{ secrets.DIGITALOCEAN_ACCESS_TOKEN }}

      - name: Login to DO Container Registry
        run: doctl registry login --expiry-seconds 1200

      - name: Build and Push Backend
        run: |
          docker build -t $REGISTRY/backend:${{ github.sha }} ./backend
          docker push $REGISTRY/backend:${{ github.sha }}

      - name: Build and Push Frontend
        run: |
          docker build -t $REGISTRY/frontend:${{ github.sha }} ./frontend
          docker push $REGISTRY/frontend:${{ github.sha }}

      - name: Configure kubectl
        run: |
          doctl kubernetes cluster kubeconfig save $CLUSTER_NAME

      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install todo-app ./helm/todo-app \
            -f ./helm/values-doks.yaml \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }} \
            -n todo-app \
            --wait

      - name: Verify Deployment
        run: |
          kubectl rollout status deployment/todo-backend -n todo-app
          kubectl rollout status deployment/todo-frontend -n todo-app
```

## Part 9: Cost Estimation & Free Tier

### DigitalOcean Cost Breakdown

| Resource | Size | Monthly Cost |
|----------|------|--------------|
| **DOKS Cluster** | 2x s-2vcpu-4gb | $24/month |
| **Load Balancer** | lb-small | $12/month |
| **Container Registry** | Basic | Free (500MB) |
| **Block Storage** | 20GB (Kafka) | $2/month |
| **Spaces** | Optional | $5/month |
| **Total** | | **~$43/month** |

### Free Tier Usage

```
╔═══════════════════════════════════════════════════════════╗
║           MAXIMIZING FREE CREDITS                          ║
╠═══════════════════════════════════════════════════════════╣
║                                                            ║
║  DigitalOcean: $200 free credit (60 days)                 ║
║  ─────────────────────────────────────────                 ║
║  • Covers ~4-5 months of basic usage                      ║
║  • Create account with GitHub for bonus                    ║
║                                                            ║
║  Cost Optimization Tips:                                   ║
║  ─────────────────────────────────────────                 ║
║  • Use smallest node size (s-2vcpu-4gb)                   ║
║  • 2 nodes minimum for HA                                  ║
║  • Use Redpanda Cloud (free) instead of Strimzi          ║
║  • Use Neon (free tier) for PostgreSQL                    ║
║  • Delete cluster when not in use (hackathon)             ║
║                                                            ║
║  Cleanup Commands:                                         ║
║  ─────────────────────────────────────────                 ║
║  doctl kubernetes cluster delete todo-cluster             ║
║  doctl registry delete todo-registry                      ║
║                                                            ║
╚═══════════════════════════════════════════════════════════╝
```

## Part 10: Cleanup & Teardown

```bash
# ═══════════════════════════════════════════════════════════════
# CLEANUP COMMANDS
# ═══════════════════════════════════════════════════════════════

# Delete Helm release
helm uninstall todo-app -n todo-app

# Delete Kafka
kubectl delete kafka todo-kafka -n kafka

# Delete Dapr
dapr uninstall -k

# Delete namespaces
kubectl delete namespace todo-app
kubectl delete namespace kafka

# Delete NGINX Ingress
helm uninstall nginx-ingress -n ingress-nginx

# Delete the cluster
doctl kubernetes cluster delete todo-cluster

# Delete container registry
doctl registry delete todo-registry

# Verify cleanup
doctl kubernetes cluster list
```

## Summary

| Step | Command/Action | Purpose |
|------|----------------|---------|
| 1 | `doctl kubernetes cluster create` | Create DOKS cluster |
| 2 | `kubectl config use-context` | Switch to cloud cluster |
| 3 | `helm upgrade --install` with cloud values | Deploy with HA settings |
| 4 | LoadBalancer service | Public access |
| 5 | `dapr init -k` | Install Dapr on cloud |
| 6 | Strimzi or Redpanda | Kafka deployment |
| 7 | `kubectl create secret` | Secrets management |
| 8 | GitHub Actions | CI/CD pipeline |

### Quick Reference

```bash
# Create cluster
doctl kubernetes cluster create todo-cluster --node-pool "name=default;size=s-2vcpu-4gb;count=2"

# Switch context
kubectl config use-context do-nyc1-todo-cluster

# Deploy
helm upgrade --install todo-app ./helm -f values-doks.yaml -n todo-app

# Get external IP
kubectl get svc -n ingress-nginx -o jsonpath='{.items[0].status.loadBalancer.ingress[0].ip}'

# Cleanup
doctl kubernetes cluster delete todo-cluster
```
