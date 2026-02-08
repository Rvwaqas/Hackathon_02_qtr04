# Phase V Part B Deployment Checklist

## Pre-Deployment Requirements

### Environment Setup
- [x] Docker daemon running
- [x] Minikube installed (v1.30+)
- [x] kubectl installed and configured
- [x] Helm 3 installed
- [x] Dapr CLI installed (v1.12+)
- [x] Phase V Part A code complete and tested

### Resource Verification
- [x] Minimum 4GB RAM available for Minikube
- [x] Minimum 2 CPUs available
- [x] Sufficient disk space (10GB+)

---

## Cluster Setup (SC-001)

### Minikube Cluster
- [x] `minikube start --memory=4096 --cpus=2 --driver=docker` succeeds
- [x] `minikube status` shows Running
- [x] `minikube addons enable ingress` succeeds
- [x] `minikube addons enable metrics-server` succeeds

### Dapr Installation
- [x] `dapr init -k --wait` completes without errors
- [x] `dapr status -k` shows all components healthy
- [x] `kubectl get pods -n dapr-system` shows all pods Running
- [x] Sidecar injector pod is Running

---

## Kafka/Redpanda Setup (SC-002)

### Redpanda Deployment
- [x] Redpanda pod deployed successfully
- [x] Pod reaches Running state
- [x] Service created on port 9092
- [x] Can exec into pod and run rpk commands

### Topic Verification
- [x] `task-events` topic exists or auto-creates
- [x] `reminders` topic exists or auto-creates
- [x] Can produce test message to topic
- [x] Can consume test message from topic

---

## Helm Deployment (SC-003)

### Chart Preparation
- [x] Dapr annotations added to backend deployment
- [x] Dapr annotations added to frontend deployment
- [x] Dapr component templates created (pubsub, state, secrets)
- [x] Redpanda deployment template created
- [x] values.yaml updated with Dapr/Kafka config
- [x] `helm lint` passes without errors

### Deployment Execution
- [x] `helm install todo-chatbot ./helm/todo-chatbot` succeeds
- [x] All pods reach Running state within 5 minutes
- [x] Backend pod shows 2/2 containers (app + sidecar)
- [x] Frontend pod shows 2/2 containers (app + sidecar)
- [x] All services created successfully

---

## Event Integration (SC-004)

### Dapr Pub/Sub Verification
- [x] `kafka-pubsub` component deployed
- [x] Backend sidecar logs show component loaded
- [x] Manual publish test via curl succeeds (204 response)
- [x] Message appears in Kafka topic

### Event Flow Testing
- [x] Create task -> `task.created` event in topic
- [x] Update task -> `task.updated` event in topic
- [x] Complete task -> `task.completed` event in topic
- [x] Delete task -> `task.deleted` event in topic
- [x] Events follow CloudEvents 1.0 schema

---

## Dapr Building Blocks (SC-005)

### Pub/Sub (pubsub.kafka)
- [x] Can publish to `task-events` topic
- [x] Can publish to `reminders` topic
- [x] Messages contain CloudEvents headers
- [x] Scoped correctly to todo-backend

### State Store (state.postgresql)
- [x] Component connects to Neon PostgreSQL
- [x] Can save state via POST
- [x] Can retrieve state via GET
- [x] State persists across pod restarts

### Secrets (secretstores.kubernetes)
- [x] Kubernetes secrets created for API keys
- [x] Can retrieve secrets via Dapr API
- [x] COHERE_API_KEY accessible
- [x] Secrets not in pod env vars

### Jobs API
- [x] Can schedule job via POST
- [x] Job appears in GET /v1.0/jobs
- [x] Callback endpoint receives trigger
- [x] Can delete job via DELETE

### Service Invocation
- [x] Frontend can invoke backend via Dapr
- [x] Health check via service invocation works

---

## Application Functionality (SC-006)

### Access Verification
- [x] `minikube service todo-frontend` opens browser
- [x] Login page loads successfully
- [x] Can authenticate with valid credentials

### Feature Testing
- [x] Dashboard displays tasks
- [x] Chatbot responds to commands
- [x] Priority feature works (chatbot + UI)
- [x] Tags feature works (chatbot + UI)
- [x] Search/filter works
- [x] Recurring tasks work
- [x] Due dates work
- [x] User isolation maintained

---

## Documentation (SC-007)

### README Documentation
- [x] Exact setup commands documented
- [x] Prerequisites listed
- [x] Step-by-step deployment guide
- [x] Verification steps included

### Technical Documentation
- [x] Helm values documented
- [x] Dapr component YAMLs explained
- [x] Architecture diagram provided
- [x] Event schema documented

### Troubleshooting
- [x] Common errors documented
- [x] Debug commands provided
- [x] Log retrieval instructions
- [x] Recovery procedures

---

## Final Validation

### End-to-End Test
- [x] Fresh Minikube cluster created
- [x] All steps executed from documentation
- [x] Application fully functional
- [x] Events flowing to Kafka
- [x] All Part A features working
- [x] Total deployment time < 15 minutes

### Cleanup Verification
- [x] `helm uninstall todo-chatbot` succeeds
- [x] `minikube delete` cleans up cluster
- [x] No orphaned resources

---

## Sign-Off

| Check | Verified By | Date |
|-------|-------------|------|
| Cluster Setup | Claude Code Agent | 2026-02-06 |
| Kafka/Redpanda | Claude Code Agent | 2026-02-06 |
| Helm Deployment | Claude Code Agent | 2026-02-06 |
| Event Integration | Claude Code Agent | 2026-02-06 |
| Dapr Building Blocks | Claude Code Agent | 2026-02-06 |
| Application Functionality | Claude Code Agent | 2026-02-06 |
| Documentation | Claude Code Agent | 2026-02-06 |
| Final Validation | Claude Code Agent | 2026-02-06 |
