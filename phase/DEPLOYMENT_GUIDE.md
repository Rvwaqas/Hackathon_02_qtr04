# AI-Powered Todo Chatbot - Deployment & Optimization Guide

Complete guide for deploying the Phase III chatbot and optimizing for production.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Environment Configuration](#environment-configuration)
3. [Database Setup](#database-setup)
4. [Performance Optimization](#performance-optimization)
5. [Deployment Strategies](#deployment-strategies)
6. [Monitoring & Observability](#monitoring--observability)
7. [Troubleshooting](#troubleshooting)

---

## Pre-Deployment Checklist

- [ ] All tests passing (`pytest backend/tests/ -v`)
- [ ] Environment variables configured (`.env` not committed)
- [ ] Database migrations applied
- [ ] SSL certificates obtained (production)
- [ ] CORS origins configured for frontend
- [ ] JWT secret key is strong (≥32 characters)
- [ ] Cohere API key has sufficient quota
- [ ] Database backups configured
- [ ] Monitoring/alerting setup complete
- [ ] API documentation reviewed
- [ ] Load testing completed
- [ ] Security scan passed

---

## Environment Configuration

### Production Environment Variables

```env
# ============ Database ============
DATABASE_URL=postgresql+asyncpg://user:strong_password@db-host.com/chatbot_db
# Use connection pooling: add ?pool_size=20&max_overflow=0

# ============ JWT Authentication ============
JWT_SECRET=your_strong_secret_key_min_32_chars_production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# ============ AI Service: Cohere ============
COHERE_API_KEY=your_cohere_api_key
COHERE_MODEL=command-r-plus

# ============ CORS Configuration ============
CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# ============ Server Configuration ============
HOST=0.0.0.0
PORT=8000
DEBUG=False  # IMPORTANT: Set to False in production

# ============ Optional: Monitoring ============
LOG_LEVEL=info
SENTRY_DSN=https://your_sentry_dsn_here
```

### Security Best Practices

1. **Never commit secrets**: Use `.env.example` template
2. **Rotate JWT secret**: Plan rotation strategy
3. **Use strong passwords**: Database password ≥24 characters
4. **Enable HTTPS**: Use SSL/TLS certificates
5. **Validate CORS**: Only allow known domains
6. **Rate limit**: Implement at reverse proxy level
7. **Input validation**: All inputs validated (already done)
8. **SQL injection prevention**: Using SQLModel ORM (safe)

---

## Database Setup

### PostgreSQL Production Setup

```bash
# 1. Create database
createdb chatbot_db

# 2. Create user with limited permissions
createuser chatbot_user
ALTER ROLE chatbot_user WITH PASSWORD 'strong_password';

# 3. Grant permissions
GRANT ALL PRIVILEGES ON DATABASE chatbot_db TO chatbot_user;

# 4. Configure connection pooling (in connection string)
# postgresql+asyncpg://user:pass@host/db?pool_size=20&max_overflow=0
```

### Database Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/chatbot"
DATE=$(date +%Y%m%d_%H%M%S)

pg_dump $DATABASE_URL > "$BACKUP_DIR/chatbot_$DATE.sql"
gzip "$BACKUP_DIR/chatbot_$DATE.sql"

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -mtime +30 -delete
```

### Migrations

```bash
# Run migrations
alembic upgrade head

# Create migration for new schema changes
alembic revision --autogenerate -m "Add new column"

# Rollback if needed
alembic downgrade -1
```

---

## Performance Optimization

### Database Optimization

1. **Connection Pooling**
```python
# In config.py
DATABASE_URL = "postgresql+asyncpg://user:pass@host/db?pool_size=20&max_overflow=0"
```

2. **Query Optimization**
```python
# Use indexes on frequently queried columns
# Conversations: user_id, (user_id, updated_at DESC)
# Messages: conversation_id, (conversation_id, created_at)
# Tasks: user_id, (user_id, status), (user_id, priority)
```

3. **Pagination**
```python
# Limit message history to 50 messages
limit=50  # in get_recent_messages()
```

### Caching Strategy

```python
# Cache Cohere model configuration
AGENT_CONFIG = {
    "model": "command-r-plus",
    "temperature": 0.7,
    "max_tokens": 1024,
    "tool_choice": "auto",
}

# Cache conversation list for 60 seconds
# Implementation: Add Redis caching layer
```

### API Response Optimization

1. **Message History**
```python
# Load last 20 messages only
messages_list = await ConversationService.get_recent_messages(
    session, conversation.id, limit=20  # Limit for performance
)
```

2. **Lazy Loading**
```python
# Don't load messages when listing conversations
# Only load when user opens conversation detail
```

3. **Compression**
```python
# Enable gzip compression at reverse proxy level
# nginx: gzip on; gzip_types application/json;
```

### Async Performance

1. **Connection Pooling**: AsyncPool with 20 connections
2. **Async I/O**: All database operations are async
3. **Concurrent Requests**: FastAPI handles automatically
4. **Timeouts**: Set reasonable timeouts

```python
# Example timeout configuration
CHAT_TIMEOUT = 30  # seconds
DATABASE_TIMEOUT = 5  # seconds
```

### Resource Limits

```python
# Memory management
# Max conversation: No limit (could add later)
# Max messages per conversation: No limit (paginated)
# Message size: 2000 characters (enforced by schema)
# Request timeout: 30 seconds (recommend in nginx)
```

---

## Deployment Strategies

### Option 1: Docker + Kubernetes

**Dockerfile**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Kubernetes Deployment**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: chatbot-api
  template:
    metadata:
      labels:
        app: chatbot-api
    spec:
      containers:
      - name: api
        image: your-registry/chatbot-api:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: chatbot-secrets
              key: database-url
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Option 2: Docker Compose (Development/Staging)

```yaml
version: '3.8'

services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/chatbot_db
      - COHERE_API_KEY=${COHERE_API_KEY}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db
    volumes:
      - ./backend:/app

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=chatbot_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Option 3: Cloud Platform (AWS, Google Cloud, Azure)

#### AWS Elastic Beanstalk
```bash
# Configure
eb init -p docker chatbot-api

# Deploy
eb create chatbot-prod
eb deploy
```

#### Google Cloud Run
```bash
# Build and deploy
gcloud run deploy chatbot-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars "DATABASE_URL=...,COHERE_API_KEY=..."
```

---

## Monitoring & Observability

### Logging

```python
# Configure logging in config.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Chat endpoint called")
logger.error("Database error", exc_info=True)
```

### Metrics to Track

1. **API Metrics**
   - Chat response time (p50, p95, p99)
   - Messages per second
   - Error rate
   - Conversation creation rate

2. **Database Metrics**
   - Connection pool usage
   - Query duration
   - Slow query log

3. **AI Service Metrics**
   - Cohere API latency
   - Tool execution time
   - Rate limit status

4. **System Metrics**
   - CPU usage
   - Memory usage
   - Disk usage
   - Network I/O

### Monitoring Tools

**Prometheus + Grafana** (Recommended):
```python
# Add to main.py
from prometheus_client import Counter, Histogram
from prometheus_client import make_asgi_app

chat_requests = Counter('chat_requests_total', 'Total chat requests')
chat_duration = Histogram('chat_duration_seconds', 'Chat request duration')
```

**Sentry** (Error Tracking):
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

### Health Check Endpoint

```python
# Already implemented in main.py
@app.get("/health")
async def health():
    return {"status": "healthy"}

# Enhanced version:
@app.get("/health/detailed")
async def health_detailed(session: AsyncSession = Depends(get_session)):
    return {
        "status": "healthy",
        "database": await check_database(session),
        "cohere": await check_cohere(),
        "timestamp": datetime.utcnow().isoformat()
    }
```

---

## Troubleshooting

### Common Issues

#### 1. Cohere API Rate Limiting

**Symptom**: "Rate limit exceeded" errors

**Solution**:
```python
# Implement retry logic
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def create_message_with_retry(self, messages, tools):
    return await self.client.chat.completions.create(...)
```

#### 2. Database Connection Timeouts

**Symptom**: "Connection pool exhausted" errors

**Solution**:
```python
# Increase pool size
DATABASE_URL = "postgresql+asyncpg://...?pool_size=30&max_overflow=10"

# Monitor pool usage
logger.info(f"Pool checkedout: {pool.checkedout()}")
```

#### 3. Memory Leaks

**Symptom**: Memory usage grows over time

**Solution**:
```python
# Ensure proper cleanup
# Use async context managers
async with session:
    # Do work
    pass  # Automatically cleaned up
```

#### 4. Slow Chat Responses

**Symptom**: Chat takes > 5 seconds

**Debug Steps**:
1. Check Cohere API latency
2. Profile database queries
3. Check tool execution time
4. Review message history size

```python
import time

start = time.time()
response = await agent.execute(message, history)
duration = time.time() - start

if duration > 5:
    logger.warning(f"Slow chat response: {duration}s")
```

---

## Load Testing

### Locust Example

```python
from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(1, 3)
    token = "your_test_token"

    @task
    def send_message(self):
        self.client.post(
            "/api/1/chat",
            json={"message": "Add a task"},
            headers={"Authorization": f"Bearer {self.token}"}
        )

    @task
    def list_conversations(self):
        self.client.get(
            "/api/1/conversations",
            headers={"Authorization": f"Bearer {self.token}"}
        )
```

**Run**:
```bash
locust -f locustfile.py -u 100 -r 10 -t 10m
```

---

## Rollback Strategy

### If Deployment Fails

```bash
# Kubernetes
kubectl rollout undo deployment/chatbot-api

# Docker Compose
docker-compose down
docker-compose up -d  # Start previous version
```

### Database Rollback

```bash
# If migrations fail
alembic downgrade -1
```

---

## Security Hardening

1. **Web Application Firewall**
   ```nginx
   # nginx config
   ModSecurity on;
   ModSecurityRuleEngine On;
   ```

2. **Rate Limiting**
   ```nginx
   limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
   limit_req zone=api burst=20 nodelay;
   ```

3. **HTTPS Only**
   ```nginx
   server {
       listen 443 ssl;
       ssl_certificate /path/to/cert;
       ssl_certificate_key /path/to/key;
   }
   ```

4. **API Key Rotation**
   - Rotate Cohere API key quarterly
   - Rotate JWT secret annually

---

## Scaling Considerations

### Horizontal Scaling

- **API Instances**: Can scale from 1 to 100+
- **Database**: Use read replicas for GET operations
- **Cache**: Add Redis for hot data

### Vertical Scaling

- Increase CPU/memory if:
  - Cohere API latency > 5s (likely external)
  - Database query time > 1s
  - Memory > 80% of available

---

## Cost Optimization

1. **Cohere API**
   - ~$0.15 per 1M input tokens
   - ~$0.60 per 1M output tokens
   - Estimated: $100-500/month for 1M messages

2. **Database**
   - Shared postgres: $50-100/month
   - Managed postgres: $200-500/month
   - Include backup costs

3. **Infrastructure**
   - 3 API instances: $300-600/month
   - CDN: $50-100/month
   - Monitoring: $50-100/month

---

## Maintenance Schedule

- **Daily**: Monitor logs and alerts
- **Weekly**: Review performance metrics
- **Monthly**: Database optimization, backups verification
- **Quarterly**: Security updates, API key rotation
- **Semi-annually**: Load testing, disaster recovery drill
- **Annually**: Security audit, JWT secret rotation

---

*Last Updated: 2024-01-15*
*Deployment Guide for Phase III Chatbot*
