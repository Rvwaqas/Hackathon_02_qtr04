# 🐳 TaskFlow Chatbot - Docker Setup Guide

> **Complete Docker setup for production-ready deployment of TaskFlow AI-Powered Todo Chatbot**

---

## 📋 Prerequisites

- **Docker**: Version 20.10+
- **Docker Compose**: Version 1.29+
- **Cohere API Key**: Get from [cohere.com](https://cohere.com)
- **Port Availability**: Ports 3000 and 8000 must be available

---

## 🚀 Quick Start (One Command)

```bash
# 1. Navigate to project
cd phase3_chatbot

# 2. Set up environment
cp .env.docker .env

# 3. Edit .env with your Cohere API key
# Replace: COHERE_API_KEY=your-cohere-api-key-here

# 4. Build and run
docker-compose up -d

# 5. Check status
docker-compose ps
```

**Frontend**: http://localhost:3000
**Backend API**: http://localhost:8000
**API Docs**: http://localhost:8000/docs

---

## 📦 File Structure

```
phase3_chatbot/
├── Dockerfile.backend          # Backend FastAPI container
├── Dockerfile.frontend         # Frontend Next.js container
├── docker-compose.yml          # Orchestration config
├── .env.docker                 # Docker environment variables
├── .dockerignore               # Docker build optimization (both)
├── backend/
│   ├── src/                    # FastAPI application
│   ├── requirements.txt        # Python dependencies
│   └── .dockerignore
└── frontend/
    ├── app/                    # Next.js pages
    ├── package.json            # Node.js dependencies
    └── .dockerignore
```

---

## 🔧 Configuration

### Set Cohere API Key

**Option 1: Environment File**
```bash
# Edit .env
COHERE_API_KEY=your-actual-key-here
```

**Option 2: Command Line**
```bash
docker-compose --env-file .env.custom up -d
```

**Option 3: Export Environment**
```bash
export COHERE_API_KEY=your-actual-key-here
docker-compose up -d
```

---

## 🎯 Common Commands

### Start Services
```bash
# Start in background
docker-compose up -d

# Start with logs visible
docker-compose up

# Start specific service
docker-compose up -d backend
docker-compose up -d frontend
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Stop Services
```bash
# Stop all
docker-compose stop

# Stop specific
docker-compose stop backend

# Stop and remove
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Rebuild
```bash
# Rebuild all
docker-compose build --no-cache

# Rebuild specific
docker-compose build --no-cache backend

# Build and start
docker-compose up -d --build
```

### Execute Commands
```bash
# Run command in backend
docker-compose exec backend python -m pytest tests/

# Run command in frontend
docker-compose exec frontend npm test

# Open shell in container
docker-compose exec backend bash
docker-compose exec frontend sh
```

---

## ✅ Health Checks

Services have built-in health checks:

```bash
# Check service health
docker-compose ps

# Watch health status
watch docker-compose ps

# Manual health check
curl http://localhost:8000/health
curl http://localhost:3000
```

---

## 🔍 Troubleshooting

### Ports Already in Use

```bash
# Find process using port 3000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Change ports in docker-compose.yml
# Change "3000:3000" to "3001:3000" to use port 3001
```

### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Check if port is in use
docker ps

# Remove and restart
docker-compose down
docker-compose up -d --build
```

### Database Connection Error

```bash
# Verify DATABASE_URL in .env
# Make sure Neon PostgreSQL is accessible

# Test connection
docker-compose exec backend python -c \
  "from src.database import engine; print('DB connected')"
```

### Cohere API Error

```bash
# Verify API key in .env
# Check Cohere API key is valid
# Visit https://dashboard.cohere.com to verify

# Test API key
docker-compose exec backend python -c \
  "from src.agents.cohere_client import CohereClient; c = CohereClient(); print('API working')"
```

### Frontend Can't Connect to Backend

```bash
# Check NEXT_PUBLIC_API_URL in .env
# Should be: http://backend:8000 (internal Docker networking)

# Verify backend is healthy
curl http://localhost:8000/health

# Check Docker network
docker network ls
docker network inspect phase3_chatbot_taskflow-network
```

---

## 📊 Performance Tuning

### Resource Limits

Edit `docker-compose.yml` to limit resources:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 512M
        reservations:
          cpus: '0.5'
          memory: 256M
```

### Database Connection Pool

In backend `.env`:
```
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=10
```

### Frontend Build Optimization

- Multi-stage build used (see `Dockerfile.frontend`)
- Production build with no dev dependencies
- Optimized bundle size

---

## 🔐 Production Security

### Change Default Secrets

```bash
# Generate new JWT secret
openssl rand -base64 32

# Update .env
JWT_SECRET=your-new-generated-secret

# Restart
docker-compose down
docker-compose up -d
```

### Set Production Mode

```env
# In .env
DEBUG=False
NODE_ENV=production
```

### Use Environment-Specific Files

```bash
# Create production env file
cp .env.docker .env.prod

# Edit with production values
vim .env.prod

# Use it
docker-compose --env-file .env.prod up -d
```

---

## 📈 Monitoring

### Container Metrics

```bash
# View real-time stats
docker stats

# View specific container
docker stats taskflow-backend
docker stats taskflow-frontend
```

### Log Aggregation

```bash
# Export logs
docker-compose logs backend > backend.log
docker-compose logs frontend > frontend.log

# Follow logs with timestamp
docker-compose logs -f --timestamps backend
```

---

## 🚢 Deployment to Cloud

### Docker Hub

```bash
# Tag images
docker tag phase3_chatbot-backend:latest myusername/taskflow-backend:latest
docker tag phase3_chatbot-frontend:latest myusername/taskflow-frontend:latest

# Push to registry
docker push myusername/taskflow-backend:latest
docker push myusername/taskflow-frontend:latest
```

### Kubernetes

```bash
# Convert docker-compose to Kubernetes manifests
kompose convert -f docker-compose.yml

# Deploy to cluster
kubectl apply -f .
```

### AWS ECS

```bash
# Use aws-cli to push and deploy
aws ecr create-repository --repository-name taskflow-backend
aws ecr create-repository --repository-name taskflow-frontend

# Tag and push
docker tag taskflow-backend:latest {ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/taskflow-backend:latest
docker push {ACCOUNT}.dkr.ecr.{REGION}.amazonaws.com/taskflow-backend:latest
```

---

## 📝 Docker-Compose Reference

### Services

**backend**
- Image: Builds from `Dockerfile.backend`
- Port: 8000
- Dependencies: None (uses Neon cloud DB)
- Health Check: HTTP `/health` endpoint

**frontend**
- Image: Builds from `Dockerfile.frontend`
- Port: 3000
- Dependencies: Waits for backend (health check)
- Health Check: HTTP GET to root

### Networks

- `taskflow-network`: Bridge network for service communication
- Services communicate via DNS: `backend`, `frontend`

### Environment Variables

Load from `.env` file or `.env.docker`

```env
# Passed to containers from docker-compose.yml
DATABASE_URL
JWT_SECRET
COHERE_API_KEY
CORS_ORIGINS
NEXT_PUBLIC_API_URL
```

---

## ✨ Best Practices

✅ **Always use `.env` file** - Never hardcode secrets
✅ **Health checks enabled** - Services verify they're working
✅ **Proper signal handling** - Graceful shutdown
✅ **Multi-stage builds** - Smaller frontend image
✅ **Volume mounts for dev** - Code hot-reloading in development
✅ **Network isolation** - Services only communicate via network
✅ **Resource limits** - Prevent container from consuming all resources

---

## 🆘 Getting Help

### Check Logs
```bash
docker-compose logs -f
```

### Verify Configuration
```bash
docker-compose config
```

### Inspect Container
```bash
docker inspect taskflow-backend
docker inspect taskflow-frontend
```

### Test Connectivity
```bash
# From backend to frontend
docker-compose exec backend curl http://frontend:3000

# From frontend to backend
docker-compose exec frontend curl http://backend:8000/health
```

---

## 📚 Resources

- [Docker Documentation](https://docs.docker.com)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [FastAPI in Containers](https://fastapi.tiangolo.com/deployment/docker/)
- [Next.js Docker](https://nextjs.org/docs/deployment)

---

**Docker setup complete! Your chatbot is ready for container deployment.** 🎉
