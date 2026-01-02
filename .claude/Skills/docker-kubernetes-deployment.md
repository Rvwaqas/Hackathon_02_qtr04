# Skill: Docker & Kubernetes Deployment

## Purpose
Containerize applications with Docker and deploy to Kubernetes (Minikube locally, cloud for production) using Helm charts.

## Tech Stack
- **Docker**: Containerization
- **Docker Compose**: Local development
- **Kubernetes**: Orchestration (Minikube / DigitalOcean DOKS)
- **Helm**: Package manager for Kubernetes
- **kubectl-ai** / **kagent**: AI-assisted K8s operations

## Phase IV: Local Kubernetes (Minikube)

### Project Structure

```
phase4/
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.backend
│   └── .dockerignore
├── docker-compose.yml          # Local development
├── helm/
│   └── todo-app/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│           ├── frontend-deployment.yaml
│           ├── frontend-service.yaml
│           ├── backend-deployment.yaml
│           ├── backend-service.yaml
│           └── ingress.yaml
└── README.md
```

### 1. Dockerfiles

**Backend Dockerfile:**
```dockerfile
# docker/Dockerfile.backend
# [Task]: T-070
# [From]: plan.md §8.1 - Containerization

FROM python:3.13-slim

WORKDIR /app

# Install UV
RUN pip install uv

# Copy dependencies first (cache layer)
COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen

# Copy application code
COPY backend/ ./

# Expose port
EXPOSE 8000

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**
```dockerfile
# docker/Dockerfile.frontend
# [Task]: T-071
# [From]: plan.md §8.1 - Containerization

FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./
RUN npm ci

# Copy source
COPY frontend/ ./

# Build
RUN npm run build

# Production image
FROM node:20-alpine

WORKDIR /app

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

**.dockerignore:**
```
# docker/.dockerignore
node_modules
.next
.git
.env
*.log
__pycache__
*.pyc
.pytest_cache
```

### 2. Docker Compose (Local Development)

```yaml
# docker-compose.yml
# [Task]: T-072
# [From]: plan.md §8.2 - Local Development Setup

version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./backend:/app  # Hot reload in development
    depends_on:
      - db

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
      - DATABASE_URL=${DATABASE_URL}
      - BETTER_AUTH_SECRET=${BETTER_AUTH_SECRET}
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next
    depends_on:
      - backend

  # Optional: Local Postgres for development
  db:
    image: postgres:16
    environment:
      - POSTGRES_USER=todo
      - POSTGRES_PASSWORD=todo123
      - POSTGRES_DB=todo_dev
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

**Usage:**
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# Stop
docker-compose down
```

### 3. Helm Chart Setup

**Chart.yaml:**
```yaml
# helm/todo-app/Chart.yaml
# [Task]: T-073
# [From]: plan.md §8.3 - Kubernetes Packaging

apiVersion: v2
name: todo-app
description: A Helm chart for Todo App (Hackathon II)
type: application
version: 1.0.0
appVersion: "1.0.0"
```

**values.yaml:**
```yaml
# helm/todo-app/values.yaml
# [Task]: T-074
# [From]: plan.md §8.3 - Kubernetes Configuration

# Frontend configuration
frontend:
  replicaCount: 2
  image:
    repository: your-dockerhub-username/todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  env:
    - name: NEXT_PUBLIC_API_URL
      value: "http://backend-service:8000"

# Backend configuration
backend:
  replicaCount: 2
  image:
    repository: your-dockerhub-username/todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  env:
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: todo-secrets
          key: database-url
    - name: BETTER_AUTH_SECRET
      valueFrom:
        secretKeyRef:
          name: todo-secrets
          key: auth-secret
    - name: OPENAI_API_KEY
      valueFrom:
        secretKeyRef:
          name: todo-secrets
          key: openai-key

# Ingress configuration
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: todo.local
      paths:
        - path: /
          pathType: Prefix
          service: frontend-service
        - path: /api
          pathType: Prefix
          service: backend-service
```

**Frontend Deployment:**
```yaml
# helm/todo-app/templates/frontend-deployment.yaml
# [Task]: T-075
# [From]: plan.md §8.4 - Kubernetes Deployments

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}-frontend
  labels:
    app: {{ .Chart.Name }}
    component: frontend
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
      component: frontend
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
        component: frontend
    spec:
      containers:
      - name: frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        imagePullPolicy: {{ .Values.frontend.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.frontend.service.port }}
        env:
        {{- range .Values.frontend.env }}
        - name: {{ .name }}
          value: {{ .value | quote }}
        {{- end }}
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

**Frontend Service:**
```yaml
# helm/todo-app/templates/frontend-service.yaml
# [Task]: T-076

apiVersion: v1
kind: Service
metadata:
  name: {{ .Chart.Name }}-frontend-service
  labels:
    app: {{ .Chart.Name }}
    component: frontend
spec:
  type: {{ .Values.frontend.service.type }}
  ports:
  - port: {{ .Values.frontend.service.port }}
    targetPort: 3000
    protocol: TCP
    name: http
  selector:
    app: {{ .Chart.Name }}
    component: frontend
```

**Backend Deployment:**
```yaml
# helm/todo-app/templates/backend-deployment.yaml
# [Task]: T-077

apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Chart.Name }}-backend
  labels:
    app: {{ .Chart.Name }}
    component: backend
spec:
  replicas: {{ .Values.backend.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
      component: backend
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
        component: backend
    spec:
      containers:
      - name: backend
        image: "{{ .Values.backend.image.repository }}:{{ .Values.backend.image.tag }}"
        imagePullPolicy: {{ .Values.backend.image.pullPolicy }}
        ports:
        - containerPort: {{ .Values.backend.service.port }}
        env:
        {{- range .Values.backend.env }}
        - name: {{ .name }}
          {{- if .value }}
          value: {{ .value | quote }}
          {{- else if .valueFrom }}
          valueFrom:
            {{- toYaml .valueFrom | nindent 12 }}
          {{- end }}
        {{- end }}
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
```

### 4. Kubernetes Secrets

```bash
# Create secrets manually
kubectl create secret generic todo-secrets \
  --from-literal=database-url="postgresql://..." \
  --from-literal=auth-secret="your-secret" \
  --from-literal=openai-key="sk-..."
```

Or use a YAML file (don't commit to Git!):
```yaml
# secrets.yaml (DO NOT COMMIT)
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
stringData:
  database-url: "postgresql://..."
  auth-secret: "your-secret"
  openai-key: "sk-..."
```

### 5. Deployment Commands

**Build and Push Images:**
```bash
# Build images
docker build -f docker/Dockerfile.backend -t your-dockerhub/todo-backend:latest .
docker build -f docker/Dockerfile.frontend -t your-dockerhub/todo-frontend:latest .

# Push to registry
docker push your-dockerhub/todo-backend:latest
docker push your-dockerhub/todo-frontend:latest
```

**Deploy to Minikube:**
```bash
# Start Minikube
minikube start --driver=docker

# Enable Ingress
minikube addons enable ingress

# Create namespace
kubectl create namespace todo-app

# Create secrets
kubectl apply -f secrets.yaml -n todo-app

# Install with Helm
helm install todo-app ./helm/todo-app -n todo-app

# Check status
kubectl get pods -n todo-app
kubectl get services -n todo-app

# Port forward (for local access)
kubectl port-forward service/todo-app-frontend-service 3000:3000 -n todo-app
kubectl port-forward service/todo-app-backend-service 8000:8000 -n todo-app
```

**Using kubectl-ai / kagent:**
```bash
# Deploy with AI assistance
kubectl-ai "deploy the todo app with 2 frontend and 2 backend replicas"

# Scale
kubectl-ai "scale the backend to handle more load"

# Debug
kubectl-ai "check why the pods are failing"

# Analyze
kagent "analyze the cluster health"
kagent "optimize resource allocation"
```

### 6. Upgrade and Rollback

```bash
# Upgrade deployment
helm upgrade todo-app ./helm/todo-app -n todo-app

# Rollback
helm rollback todo-app -n todo-app

# View history
helm history todo-app -n todo-app
```

## Best Practices

### 1. Multi-Stage Builds
```dockerfile
# ✅ Good - Smaller final image
FROM node:20-alpine AS builder
RUN npm run build

FROM node:20-alpine
COPY --from=builder /app/.next ./.next
```

### 2. Health Checks
```yaml
# ✅ Good - K8s can restart failed containers
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
```

### 3. Resource Limits
```yaml
# ✅ Good - Prevent resource exhaustion
resources:
  requests:
    memory: "256Mi"
    cpu: "200m"
  limits:
    memory: "1Gi"
    cpu: "1000m"
```

### 4. Use Secrets for Sensitive Data
```yaml
# ✅ Good - Secrets from K8s
env:
  - name: DATABASE_URL
    valueFrom:
      secretKeyRef:
        name: todo-secrets
        key: database-url

# ❌ Bad - Hardcoded secrets
env:
  - name: DATABASE_URL
    value: "postgresql://user:pass@..."
```

## Summary

This skill provides:
- ✅ Production-ready Dockerfiles
- ✅ Docker Compose for local development
- ✅ Helm charts for Kubernetes deployment
- ✅ Multi-replica deployments
- ✅ Health checks and resource limits
- ✅ Secret management
- ✅ kubectl-ai / kagent AI-assisted ops
- ✅ Minikube local deployment
- ✅ Cloud deployment ready (Phase V)