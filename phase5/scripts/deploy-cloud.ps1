# Phase V Part C - Cloud Deploy Script (Windows PowerShell)
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
#   .\scripts\deploy-cloud.ps1 `
#     -BrokerUrl "<REDPANDA_BOOTSTRAP_URL>:9092" `
#     -DatabaseUrl "<NEON_URL>" `
#     -CohereKey "<COHERE_API_KEY>" `
#     -JwtSecret "<JWT_SECRET>"

param(
    [Parameter(Mandatory=$true)]
    [string]$BrokerUrl,

    [Parameter(Mandatory=$true)]
    [string]$DatabaseUrl,

    [Parameter(Mandatory=$true)]
    [string]$CohereKey,

    [Parameter(Mandatory=$true)]
    [string]$JwtSecret,

    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

function Log($msg) { Write-Host "[DEPLOY] $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "[WARN] $msg" -ForegroundColor Yellow }
function Error($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Phase5Dir = Split-Path -Parent $ScriptDir
$ChartDir = Join-Path $Phase5Dir "helm\todo-chatbot"

Log "Phase V Part C - Cloud Deployment to Oracle OKE"
Log "================================================"

# Step 1: Verify kubectl connectivity
Log "Step 1: Verifying kubectl connectivity..."
try { kubectl get nodes } catch { Error "Cannot connect to cluster. Run: oci ce cluster create-kubeconfig ..." }

# Step 2: Verify Dapr
Log "Step 2: Verifying Dapr installation..."
try { dapr status -k } catch { Error "Dapr not installed. Run: dapr init -k --wait" }

# Step 3: Deploy with Helm
Log "Step 3: Deploying with Helm (cloud values)..."
helm upgrade --install todo-chatbot $ChartDir `
  -f "$ChartDir\values.yaml" `
  -f "$ChartDir\values-cloud.yaml" `
  --set "backend.image.tag=$ImageTag" `
  --set "frontend.image.tag=$ImageTag" `
  --set "kafka.brokerUrl=$BrokerUrl" `
  --set "secrets.databaseUrl=$DatabaseUrl" `
  --set "secrets.cohereApiKey=$CohereKey" `
  --set "secrets.jwtSecret=$JwtSecret" `
  --wait --timeout 300s

Log "Step 4: Verifying deployment..."
kubectl get pods
kubectl get svc

# Step 5: Check LoadBalancer IP
Log "Step 5: Checking LoadBalancer external IP..."
$ExternalIp = kubectl get svc todo-chatbot-frontend -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>$null
if ($ExternalIp) {
    Log "Frontend accessible at: http://${ExternalIp}:3000"
} else {
    Warn "LoadBalancer IP not yet assigned. Run: kubectl get svc -w"
}

Log "Deployment complete!"
