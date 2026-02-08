# Phase V Part B - One-Click Minikube + Dapr + Kafka Deployment
# Usage: .\scripts\deploy.ps1
# Prerequisites: Docker Desktop, Minikube, Helm, Dapr CLI installed

param(
    [string]$DatabaseUrl = "",
    [string]$CohereApiKey = "",
    [string]$JwtSecret = "dev-jwt-secret-change-in-production",
    [switch]$SkipMinikube,
    [switch]$SkipDapr,
    [switch]$SkipBuild,
    [switch]$CleanupOnly
)

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Phase5Dir = Split-Path -Parent $ScriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Phase V Part B - Deployment Script" -ForegroundColor Cyan
Write-Host " Minikube + Dapr + Kafka (Redpanda)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# --- Cleanup Mode ---
if ($CleanupOnly) {
    Write-Host "[CLEANUP] Removing deployment..." -ForegroundColor Yellow
    helm uninstall todo-chatbot 2>$null
    kubectl delete secret todo-chatbot-secrets 2>$null
    dapr uninstall -k 2>$null
    minikube stop 2>$null
    Write-Host "[CLEANUP] Done." -ForegroundColor Green
    exit 0
}

# --- Step 1: Prerequisites Check ---
Write-Host "[1/8] Checking prerequisites..." -ForegroundColor Yellow

$tools = @{
    "docker"   = "docker --version"
    "minikube" = "minikube version"
    "kubectl"  = "kubectl version --client"
    "helm"     = "helm version --short"
    "dapr"     = "dapr --version"
}

foreach ($tool in $tools.GetEnumerator()) {
    try {
        Invoke-Expression $tool.Value | Out-Null
        Write-Host "  [OK] $($tool.Key)" -ForegroundColor Green
    }
    catch {
        Write-Host "  [MISSING] $($tool.Key) - Please install before proceeding" -ForegroundColor Red
        exit 1
    }
}

# --- Step 2: Start Minikube ---
if (-not $SkipMinikube) {
    Write-Host ""
    Write-Host "[2/8] Starting Minikube cluster..." -ForegroundColor Yellow
    $minikubeStatus = minikube status 2>&1 | Select-String "Running"
    if ($minikubeStatus) {
        Write-Host "  Minikube already running" -ForegroundColor Green
    }
    else {
        minikube start --memory=4096 --cpus=2 --driver=docker
        Write-Host "  Minikube started" -ForegroundColor Green
    }

    Write-Host "  Enabling addons..." -ForegroundColor Gray
    minikube addons enable ingress 2>$null
    minikube addons enable metrics-server 2>$null
}
else {
    Write-Host ""
    Write-Host "[2/8] Skipping Minikube (--SkipMinikube)" -ForegroundColor Gray
}

# --- Step 3: Install Dapr ---
if (-not $SkipDapr) {
    Write-Host ""
    Write-Host "[3/8] Installing Dapr on cluster..." -ForegroundColor Yellow
    $daprStatus = dapr status -k 2>&1 | Select-String "Running"
    if ($daprStatus) {
        Write-Host "  Dapr already installed" -ForegroundColor Green
    }
    else {
        dapr init -k --wait
        Write-Host "  Dapr installed" -ForegroundColor Green
    }
    dapr status -k
}
else {
    Write-Host ""
    Write-Host "[3/8] Skipping Dapr (--SkipDapr)" -ForegroundColor Gray
}

# --- Step 4: Configure Docker for Minikube ---
Write-Host ""
Write-Host "[4/8] Configuring Docker for Minikube..." -ForegroundColor Yellow
& minikube -p minikube docker-env --shell powershell | Invoke-Expression
Write-Host "  Docker env set to Minikube" -ForegroundColor Green

# --- Step 5: Build Docker Images ---
if (-not $SkipBuild) {
    Write-Host ""
    Write-Host "[5/8] Building Docker images..." -ForegroundColor Yellow

    Write-Host "  Building backend image..." -ForegroundColor Gray
    docker build -t todo-backend:latest -f "$Phase5Dir/docker/Dockerfile.backend" "$Phase5Dir"
    Write-Host "  Backend image built" -ForegroundColor Green

    Write-Host "  Building frontend image..." -ForegroundColor Gray
    docker build -t todo-frontend:latest -f "$Phase5Dir/docker/Dockerfile.frontend" "$Phase5Dir"
    Write-Host "  Frontend image built" -ForegroundColor Green
}
else {
    Write-Host ""
    Write-Host "[5/8] Skipping Docker build (--SkipBuild)" -ForegroundColor Gray
}

# --- Step 6: Create Kubernetes Secrets ---
Write-Host ""
Write-Host "[6/8] Creating Kubernetes secrets..." -ForegroundColor Yellow

# Check if secrets already exist
$existingSecrets = kubectl get secret todo-chatbot-secrets 2>&1
if ($existingSecrets -notmatch "NotFound") {
    Write-Host "  Secrets already exist, skipping" -ForegroundColor Green
}
else {
    if (-not $DatabaseUrl) {
        $DatabaseUrl = Read-Host "  Enter DATABASE_URL (Neon PostgreSQL connection string)"
    }
    if (-not $CohereApiKey) {
        $CohereApiKey = Read-Host "  Enter COHERE_API_KEY"
    }

    kubectl create secret generic todo-chatbot-secrets `
        --from-literal=database-url="$DatabaseUrl" `
        --from-literal=cohere-api-key="$CohereApiKey" `
        --from-literal=jwt-secret="$JwtSecret"
    Write-Host "  Secrets created" -ForegroundColor Green
}

# --- Step 7: Deploy with Helm ---
Write-Host ""
Write-Host "[7/8] Deploying with Helm..." -ForegroundColor Yellow

helm upgrade --install todo-chatbot "$Phase5Dir/helm/todo-chatbot" `
    -f "$Phase5Dir/helm/todo-chatbot/values-dapr.yaml" `
    --wait --timeout 5m

Write-Host "  Helm deployment complete" -ForegroundColor Green

# --- Step 8: Verification ---
Write-Host ""
Write-Host "[8/8] Verifying deployment..." -ForegroundColor Yellow

Write-Host ""
Write-Host "--- Pod Status ---" -ForegroundColor Cyan
kubectl get pods

Write-Host ""
Write-Host "--- Services ---" -ForegroundColor Cyan
kubectl get svc

Write-Host ""
Write-Host "--- Dapr Components ---" -ForegroundColor Cyan
kubectl get components.dapr.io 2>$null

Write-Host ""
Write-Host "--- Dapr Status ---" -ForegroundColor Cyan
dapr status -k

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "  minikube service todo-chatbot-frontend --url" -ForegroundColor White
Write-Host ""
Write-Host "Test Pub/Sub:" -ForegroundColor Cyan
Write-Host '  kubectl exec deploy/todo-chatbot-backend -c todo-backend -- curl -s -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events -H "Content-Type: application/json" -d "{\"specversion\":\"1.0\",\"type\":\"com.todo.task.test\",\"source\":\"/test\",\"id\":\"test-1\",\"data\":{\"test\":true}}"' -ForegroundColor White
Write-Host ""
Write-Host "Cleanup:" -ForegroundColor Cyan
Write-Host "  .\scripts\deploy.ps1 -CleanupOnly" -ForegroundColor White
