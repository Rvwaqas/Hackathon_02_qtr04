# Quickstart: Phase V Part C - Cloud Deployment on Oracle OKE

## Prerequisites

- Oracle Cloud account (Always Free): https://www.oracle.com/cloud/free/
- Redpanda Cloud account (free): https://redpanda.com/cloud
- OCI CLI installed: `brew install oci-cli` or `pip install oci-cli`
- Docker with buildx support
- Helm 3.x installed
- kubectl installed
- GitHub account with Actions enabled

## Step 1: Create OKE Cluster (Oracle Console)

1. Login to Oracle Cloud Console
2. Navigate: Developer Services → Kubernetes Clusters (OKE)
3. Create Cluster → Quick Create
4. Settings:
   - Name: `todo-chatbot-cluster`
   - Kubernetes Version: 1.28+
   - Shape: VM.Standard.A1.Flex (Always Free)
   - OCPUs: 2 per node
   - Memory: 12 GB per node
   - Nodes: 2
5. Click Create (takes ~10 minutes)

## Step 2: Configure kubectl

```bash
oci ce cluster create-kubeconfig \
  --cluster-id <CLUSTER_OCID> \
  --file $HOME/.kube/config \
  --region <REGION> \
  --token-version 2.0.0

kubectl get nodes  # Should show 2 Ready nodes
```

## Step 3: Install Dapr

```bash
dapr init -k --wait
dapr status -k  # All components healthy
```

## Step 4: Setup Redpanda Cloud

1. Login to Redpanda Cloud Console
2. Create Serverless Cluster (free tier)
3. Create topics: `task-events`, `reminders`, `task-updates`
4. Create SASL user: note username and password
5. Note bootstrap URL

## Step 5: Create Kubernetes Secrets

```bash
kubectl create secret generic kafka-secrets \
  --from-literal=username=<REDPANDA_USER> \
  --from-literal=password=<REDPANDA_PASSWORD>

kubectl create secret generic todo-secrets \
  --from-literal=database-url=<NEON_URL> \
  --from-literal=cohere-api-key=<COHERE_KEY> \
  --from-literal=jwt-secret=<JWT_SECRET>
```

## Step 6: Build & Push Docker Images

```bash
docker buildx create --name multiarch --use

# Backend
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.backend \
  -t ghcr.io/<owner>/todo-backend:latest --push .

# Frontend
docker buildx build --platform linux/amd64,linux/arm64 \
  -f docker/Dockerfile.frontend \
  -t ghcr.io/<owner>/todo-frontend:latest --push .
```

## Step 7: Deploy with Helm

```bash
helm upgrade --install todo-chatbot ./helm/todo-chatbot \
  -f ./helm/todo-chatbot/values.yaml \
  -f ./helm/todo-chatbot/values-cloud.yaml \
  --set kafka.brokerUrl="<REDPANDA_BOOTSTRAP_URL>:9092" \
  --set secrets.databaseUrl="<NEON_URL>" \
  --set secrets.cohereApiKey="<COHERE_KEY>" \
  --set secrets.jwtSecret="<JWT_SECRET>"
```

## Step 8: Get Public URL

```bash
kubectl get svc  # Wait for EXTERNAL-IP
# Open http://<EXTERNAL-IP>:3000 in browser
```

## Step 9: Verify

- Login and create a task via chatbot
- Check Redpanda Cloud console for events
- Check `kubectl logs <pod> -c daprd` for Dapr activity

## Step 10: Setup CI/CD (optional)

1. Add GitHub repository secrets (see plan.md Phase 7)
2. Push `.github/workflows/deploy-cloud.yml`
3. Push to main branch → workflow auto-deploys
