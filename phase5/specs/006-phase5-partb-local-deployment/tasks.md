# Tasks: Phase V Part B - Local Minikube + Dapr + Kafka Deployment

**Feature ID**: 006-phase5-partb-local-deployment
**Version**: 1.0.0
**Created**: 2026-02-04
**Total Tasks**: 45
**Execution Mode**: Sequential (AI-Agent Assisted)

---

## Overview

This task breakdown deploys the Phase V application with full Dapr runtime and local Kafka (Redpanda) on Minikube. Tasks are organized by user story from the specification.

**Key Principle**: All infrastructure operations via AI agents (kubectl-ai, kagent) - no manual kubectl/helm commands.

---

## Phase 1: Environment Setup & Verification

**Goal**: Verify prerequisites and Phase IV baseline works

### Tasks

- [X] T601 [US1] Verify Minikube cluster is running with `minikube status`
  - **Agent**: K8sAgent
  - **Command**: `minikube status`
  - **Expected**: Host, kubelet, apiserver all Running
  - **If not running**: `minikube start --memory=4096 --cpus=2 --driver=docker`

- [X] T602 [US1] Enable required Minikube addons
  - **Agent**: K8sAgent
  - **Commands**:
    ```bash
    minikube addons enable ingress
    minikube addons enable metrics-server
    ```
  - **Verification**: `minikube addons list | grep enabled`

- [X] T603 [US1] Verify Dapr CLI is installed
  - **Agent**: K8sAgent
  - **Command**: `dapr --version`
  - **Expected**: Dapr CLI version 1.12+
  - **If not installed**: Follow https://docs.dapr.io/getting-started/install-dapr-cli/

- [X] T604 [US1] Verify Phase IV Helm chart exists
  - **Agent**: HelmAgent
  - **Command**: `ls -la phase4_chatbot/helm/todo-chatbot/`
  - **Expected**: Chart.yaml, values.yaml, templates/ present
  - **Output**: List all template files

**Gate**: All prerequisites verified ✓

---

## Phase 2: Dapr Runtime Installation

**Goal**: Install and verify Dapr on Minikube cluster (US-001, US-003)

### Tasks

- [X] T605 [US1] Install Dapr on Minikube cluster
  - **Agent**: K8sAgent
  - **Command**: `dapr init -k --wait`
  - **Expected**: All Dapr components installed in dapr-system namespace
  - **Timeout**: 5 minutes

- [X] T606 [US1] Verify Dapr system components healthy
  - **Agent**: K8sAgent
  - **Command**: `dapr status -k`
  - **Expected Output**:
    ```
    NAME                   NAMESPACE    HEALTHY  STATUS   REPLICAS  VERSION  AGE
    dapr-operator          dapr-system  True     Running  1         1.12.x   ...
    dapr-sidecar-injector  dapr-system  True     Running  1         1.12.x   ...
    dapr-placement-server  dapr-system  True     Running  1         1.12.x   ...
    dapr-sentry            dapr-system  True     Running  1         1.12.x   ...
    ```

- [X] T607 [US1] Verify Dapr pods running
  - **Agent**: K8sAgent
  - **Command**: `kubectl get pods -n dapr-system`
  - **Expected**: All pods in Running state, 1/1 ready

**Gate**: `dapr status -k` shows all components healthy ✓

---

## Phase 3: Kafka (Redpanda) Deployment

**Goal**: Deploy local Kafka broker for event streaming (US-002)

### Tasks

- [X] T608 [US2] Create Helm templates directory for Kafka
  - **Agent**: HelmAgent
  - **Command**: `mkdir -p phase5/helm/todo-chatbot/templates/kafka`
  - **Files**: Create directory structure

- [X] T609 [US2] Create Redpanda deployment YAML
  - **Agent**: HelmAgent
  - **File**: `phase5/helm/todo-chatbot/templates/kafka/redpanda-deployment.yaml`
  - **Content**:
    ```yaml
    {{- if .Values.kafka.enabled }}
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: redpanda
      labels:
        app: redpanda
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: redpanda
      template:
        metadata:
          labels:
            app: redpanda
        spec:
          containers:
          - name: redpanda
            image: {{ .Values.redpanda.image.repository }}:{{ .Values.redpanda.image.tag }}
            command:
              - redpanda
              - start
              - --smp
              - "1"
              - --mode
              - dev-container
              - --advertise-kafka-addr
              - internal://redpanda.default.svc.cluster.local:9092
            ports:
            - containerPort: 9092
              name: kafka
            resources:
              limits:
                memory: {{ .Values.redpanda.resources.limits.memory }}
                cpu: {{ .Values.redpanda.resources.limits.cpu }}
    {{- end }}
    ```

- [X] T610 [US2] Create Redpanda service YAML
  - **Agent**: HelmAgent
  - **File**: `phase5/helm/todo-chatbot/templates/kafka/redpanda-service.yaml`
  - **Content**:
    ```yaml
    {{- if .Values.kafka.enabled }}
    apiVersion: v1
    kind: Service
    metadata:
      name: redpanda
    spec:
      selector:
        app: redpanda
      ports:
      - port: 9092
        targetPort: 9092
        name: kafka
    {{- end }}
    ```

- [X] T611 [US2] Deploy Redpanda to cluster
  - **Agent**: K8sAgent
  - **Note**: Will be deployed with Helm in Phase 5
  - **Verification**: Pod creation deferred to Helm install

**Gate**: Redpanda templates created ✓

---

## Phase 4: Helm Chart Extension for Dapr

**Goal**: Add Dapr sidecar annotations to deployments (US-001, US-003)

### Tasks

- [X] T612 [US1] Copy Phase IV Helm chart to Phase 5
  - **Agent**: HelmAgent
  - **Command**: `cp -r phase4_chatbot/helm/todo-chatbot phase5/helm/`
  - **Verification**: `ls phase5/helm/todo-chatbot/`

- [X] T613 [US1] Update backend deployment with Dapr annotations
  - **Agent**: HelmAgent
  - **File**: `phase5/helm/todo-chatbot/templates/backend-deployment.yaml`
  - **Add to spec.template.metadata**:
    ```yaml
    annotations:
      {{- if .Values.backend.dapr.enabled }}
      dapr.io/enabled: "true"
      dapr.io/app-id: "{{ .Values.backend.dapr.appId }}"
      dapr.io/app-port: "{{ .Values.backend.dapr.appPort }}"
      dapr.io/log-level: "{{ .Values.dapr.logLevel }}"
      dapr.io/enable-api-logging: "true"
      {{- end }}
    ```

- [X] T614 [US1] Update frontend deployment with Dapr annotations
  - **Agent**: HelmAgent
  - **File**: `phase5/helm/todo-chatbot/templates/frontend-deployment.yaml`
  - **Add to spec.template.metadata**:
    ```yaml
    annotations:
      {{- if .Values.frontend.dapr.enabled }}
      dapr.io/enabled: "true"
      dapr.io/app-id: "{{ .Values.frontend.dapr.appId }}"
      dapr.io/app-port: "{{ .Values.frontend.dapr.appPort }}"
      dapr.io/log-level: "{{ .Values.dapr.logLevel }}"
      {{- end }}
    ```

- [X] T615 [US1] Create values-dapr.yaml configuration
  - **Agent**: HelmAgent
  - **File**: `phase5/helm/todo-chatbot/values-dapr.yaml`
  - **Content**:
    ```yaml
    # Dapr Configuration for Phase V Part B
    dapr:
      enabled: true
      logLevel: info

    backend:
      dapr:
        enabled: true
        appId: todo-backend
        appPort: 8000

    frontend:
      dapr:
        enabled: true
        appId: todo-frontend
        appPort: 3000

    kafka:
      enabled: true
      broker: redpanda

    redpanda:
      enabled: true
      image:
        repository: docker.redpanda.com/redpandadata/redpanda
        tag: v23.3.5
      resources:
        limits:
          memory: 1Gi
          cpu: "1"
    ```

- [X] T616 [US1] Update Chart.yaml with Part B version
  - **Agent**: HelmAgent
  - **File**: `phase5/helm/todo-chatbot/Chart.yaml`
  - **Update**:
    ```yaml
    version: 2.0.0
    appVersion: "5.0.0-partb"
    description: Todo Chatbot with Dapr and Kafka integration
    ```

- [X] T617 [US1] Validate Helm chart with lint
  - **Agent**: HelmAgent
  - **Command**: `helm lint phase5/helm/todo-chatbot`
  - **Expected**: No errors

- [X] T618 [US1] Render templates to verify Dapr annotations
  - **Agent**: HelmAgent
  - **Command**: `helm template todo-chatbot phase5/helm/todo-chatbot -f phase5/helm/todo-chatbot/values-dapr.yaml > rendered.yaml`
  - **Verification**: Search for `dapr.io/enabled: "true"` in output

**Gate**: `helm lint` passes, annotations visible in rendered YAML ✓

---

## Phase 5: Dapr Components Configuration

**Goal**: Configure Dapr building blocks (US-003, US-005, US-006)

### Tasks

- [X] T619 [US3] Create Dapr templates directory
  - **Agent**: HelmAgent
  - **Command**: `mkdir -p phase5/helm/todo-chatbot/templates/dapr`

- [X] T620 [US3] Create kafka-pubsub component template
  - **Agent**: DaprAgent
  - **File**: `phase5/helm/todo-chatbot/templates/dapr/pubsub-kafka.yaml`
  - **Content**:
    ```yaml
    {{- if and .Values.dapr.enabled .Values.kafka.enabled }}
    apiVersion: dapr.io/v1alpha1
    kind: Component
    metadata:
      name: kafka-pubsub
    spec:
      type: pubsub.kafka
      version: v1
      metadata:
        - name: brokers
          value: "redpanda.default.svc.cluster.local:9092"
        - name: consumerGroup
          value: "todo-app"
        - name: authRequired
          value: "false"
        - name: initialOffset
          value: "newest"
    scopes:
      - todo-backend
    {{- end }}
    ```

- [X] T621 [US5] Create statestore component template
  - **Agent**: DaprAgent
  - **File**: `phase5/helm/todo-chatbot/templates/dapr/statestore.yaml`
  - **Content**:
    ```yaml
    {{- if .Values.dapr.enabled }}
    apiVersion: dapr.io/v1alpha1
    kind: Component
    metadata:
      name: statestore
    spec:
      type: state.postgresql
      version: v1
      metadata:
        - name: connectionString
          secretKeyRef:
            name: db-secrets
            key: connection-string
        - name: tableName
          value: "dapr_state"
    scopes:
      - todo-backend
    {{- end }}
    ```

- [X] T622 [US6] Create kubernetes-secrets component template
  - **Agent**: DaprAgent
  - **File**: `phase5/helm/todo-chatbot/templates/dapr/secretstore.yaml`
  - **Content**:
    ```yaml
    {{- if .Values.dapr.enabled }}
    apiVersion: dapr.io/v1alpha1
    kind: Component
    metadata:
      name: kubernetes-secrets
    spec:
      type: secretstores.kubernetes
      version: v1
      metadata: []
    {{- end }}
    ```

- [X] T623 [US6] Create Kubernetes secrets for API keys
  - **Agent**: K8sAgent
  - **Commands**:
    ```bash
    kubectl create secret generic db-secrets \
      --from-literal=connection-string="$DATABASE_URL" \
      --dry-run=client -o yaml > phase5/k8s/secrets/db-secrets.yaml

    kubectl create secret generic api-secrets \
      --from-literal=cohere-api-key="$COHERE_API_KEY" \
      --from-literal=gemini-api-key="$GEMINI_API_KEY" \
      --from-literal=better-auth-secret="$BETTER_AUTH_SECRET" \
      --dry-run=client -o yaml > phase5/k8s/secrets/api-secrets.yaml
    ```
  - **Note**: User must provide actual values before applying

**Gate**: Dapr component templates created ✓

---

## Phase 6: Application Deployment

**Goal**: Deploy full application with Dapr sidecars (US-001, US-007)

### Tasks

- [X] T624 [US1] Build backend Docker image for Minikube
  - **Agent**: K8sAgent
  - **Commands**:
    ```bash
    eval $(minikube docker-env)
    docker build -t todo-backend:latest phase5/backend/
    ```
  - **Verification**: `docker images | grep todo-backend`

- [X] T625 [US1] Build frontend Docker image for Minikube
  - **Agent**: K8sAgent
  - **Commands**:
    ```bash
    eval $(minikube docker-env)
    docker build -t todo-frontend:latest phase5/frontend/
    ```
  - **Verification**: `docker images | grep todo-frontend`

- [X] T626 [US6] Apply Kubernetes secrets
  - **Agent**: K8sAgent
  - **Commands**:
    ```bash
    kubectl apply -f phase5/k8s/secrets/db-secrets.yaml
    kubectl apply -f phase5/k8s/secrets/api-secrets.yaml
    ```
  - **Verification**: `kubectl get secrets`

- [X] T627 [US1] Deploy application with Helm
  - **Agent**: K8sAgent
  - **Command**:
    ```bash
    helm upgrade --install todo-chatbot phase5/helm/todo-chatbot \
      -f phase5/helm/todo-chatbot/values-dapr.yaml \
      --set backend.image.repository=todo-backend \
      --set backend.image.tag=latest \
      --set frontend.image.repository=todo-frontend \
      --set frontend.image.tag=latest
    ```
  - **Timeout**: 5 minutes

- [X] T628 [US1] Verify pods have Dapr sidecars (2/2 containers)
  - **Agent**: K8sAgent
  - **Command**: `kubectl get pods`
  - **Expected**:
    ```
    NAME                             READY   STATUS    RESTARTS   AGE
    todo-backend-xxx                 2/2     Running   0          ...
    todo-frontend-xxx                2/2     Running   0          ...
    redpanda-xxx                     1/1     Running   0          ...
    ```

- [X] T629 [US1] Verify Dapr components deployed
  - **Agent**: K8sAgent
  - **Command**: `kubectl get components.dapr.io`
  - **Expected**:
    ```
    NAME                 AGE
    kafka-pubsub         ...
    statestore           ...
    kubernetes-secrets   ...
    ```

- [X] T630 [US1] Check Dapr sidecar logs for backend
  - **Agent**: K8sAgent
  - **Command**: `kubectl logs -l app=todo-backend -c daprd --tail=50`
  - **Expected**: "component loaded" messages, no errors

**Gate**: All pods Running with 2/2 containers, components loaded ✓

---

## Phase 7: Kafka & Event Integration Verification

**Goal**: Verify event publishing to Kafka (US-002, US-003)

### Tasks

- [X] T631 [US2] Verify Redpanda pod is running
  - **Agent**: KafkaAgent
  - **Command**: `kubectl get pods -l app=redpanda`
  - **Expected**: Running, 1/1 ready

- [X] T632 [US2] Check Redpanda logs for startup
  - **Agent**: KafkaAgent
  - **Command**: `kubectl logs -l app=redpanda --tail=30`
  - **Expected**: Broker started, listening on 9092

- [X] T633 [US3] Test manual publish via Dapr sidecar
  - **Agent**: DaprAgent
  - **Command**:
    ```bash
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl -X POST http://localhost:3500/v1.0/publish/kafka-pubsub/task-events \
      -H "Content-Type: application/json" \
      -d '{"specversion":"1.0","type":"com.todo.task.test","source":"/test","id":"test-123","data":{"test":"message"}}'
    ```
  - **Expected**: HTTP 204 (no content = success)

- [X] T634 [US2] Verify message in Kafka topic
  - **Agent**: KafkaAgent
  - **Command**:
    ```bash
    kubectl exec -it deployment/redpanda -- \
      rpk topic consume task-events -n 1 --brokers localhost:9092
    ```
  - **Expected**: JSON message with test data

- [X] T635 [US2] Create task via application and verify event
  - **Agent**: OrchestratorAgent
  - **Steps**:
    1. Open app: `minikube service todo-frontend --url`
    2. Login and create a task
    3. Run: `kubectl exec -it deployment/redpanda -- rpk topic consume task-events -n 1`
  - **Expected**: `com.todo.task.created` event in topic

**Gate**: Events visible in Kafka with CloudEvents format ✓

---

## Phase 8: Dapr Building Blocks Testing

**Goal**: Verify all 5 Dapr building blocks (US-003, US-004, US-005, US-006)

### Tasks

- [X] T636 [US3] Test Pub/Sub building block
  - **Agent**: DaprAgent
  - **Test**: Publish and verify message
  - **Status**: Already verified in Phase 7

- [X] T637 [US5] Test State Store building block
  - **Agent**: DaprAgent
  - **Commands**:
    ```bash
    # Save state
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl -X POST http://localhost:3500/v1.0/state/statestore \
      -H "Content-Type: application/json" \
      -d '[{"key":"test-key","value":{"message":"hello dapr"}}]'

    # Get state
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl http://localhost:3500/v1.0/state/statestore/test-key
    ```
  - **Expected**: `{"message":"hello dapr"}`

- [X] T638 [US6] Test Secrets building block
  - **Agent**: DaprAgent
  - **Command**:
    ```bash
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl http://localhost:3500/v1.0/secrets/kubernetes-secrets/api-secrets
    ```
  - **Expected**: JSON with secret keys (values not shown in logs)

- [X] T639 [US4] Test Jobs API building block
  - **Agent**: DaprAgent
  - **Commands**:
    ```bash
    # Schedule a job
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl -X POST http://localhost:3500/v1.0/jobs/test-job \
      -H "Content-Type: application/json" \
      -d '{"schedule":"@every 1m","data":{"test":"job"}}'

    # List jobs
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl http://localhost:3500/v1.0/jobs

    # Delete job
    kubectl exec -it deployment/todo-backend -c todo-backend -- \
      curl -X DELETE http://localhost:3500/v1.0/jobs/test-job
    ```
  - **Expected**: Job created, listed, deleted

- [X] T640 [P] Test Service Invocation building block
  - **Agent**: DaprAgent
  - **Command**:
    ```bash
    kubectl exec -it deployment/todo-frontend -c todo-frontend -- \
      curl http://localhost:3500/v1.0/invoke/todo-backend/method/api/health
    ```
  - **Expected**: Health check response from backend

**Gate**: All 5 Dapr building blocks functional ✓

---

## Phase 9: End-to-End Application Testing

**Goal**: Full application functionality verification (US-007)

### Tasks

- [X] T641 [US7] Access frontend via Minikube service
  - **Agent**: OrchestratorAgent
  - **Command**: `minikube service todo-frontend --url`
  - **Expected**: URL opens in browser, login page displayed

- [X] T642 [US7] Test login flow
  - **Agent**: OrchestratorAgent
  - **Steps**:
    1. Navigate to login page
    2. Enter valid credentials
    3. Verify dashboard loads
  - **Expected**: Dashboard with task list displayed

- [X] T643 [US7] Test chatbot with Phase V Part A features
  - **Agent**: OrchestratorAgent
  - **Test Commands**:
    ```
    "add high priority task Review PR"
    "add task Meeting #work"
    "show high priority tasks"
    "search tasks for Meeting"
    "add daily task Standup"
    ```
  - **Expected**: All commands execute successfully

- [X] T644 [US7] Verify events published for task operations
  - **Agent**: OrchestratorAgent
  - **After each chatbot command, verify**:
    ```bash
    kubectl exec -it deployment/redpanda -- \
      rpk topic consume task-events -n 1 --brokers localhost:9092
    ```
  - **Expected**: CloudEvents for each operation

- [X] T645 [US7] Verify user isolation maintained
  - **Agent**: OrchestratorAgent
  - **Test**: Create tasks with different users, verify isolation
  - **Expected**: Users only see their own tasks

**Gate**: Full application functional in Minikube ✓

---

## Phase 10: Documentation & Cleanup

**Goal**: Complete deployment documentation (US-008)

### Tasks

- [X] T646 [US8] Create deployment README
  - **Agent**: OrchestratorAgent
  - **File**: `phase5/DEPLOYMENT.md`
  - **Content**:
    - Prerequisites
    - Quick start commands
    - Verification steps
    - Architecture diagram

- [X] T647 [US8] Document Helm values configuration
  - **Agent**: OrchestratorAgent
  - **File**: `phase5/helm/todo-chatbot/README.md`
  - **Content**: All values with descriptions

- [X] T648 [US8] Document Dapr component configurations
  - **Agent**: OrchestratorAgent
  - **File**: `phase5/docs/dapr-components.md`
  - **Content**: Each component with usage examples

- [X] T649 [US8] Create troubleshooting guide
  - **Agent**: OrchestratorAgent
  - **File**: `phase5/docs/troubleshooting.md`
  - **Content**: Common errors and solutions

- [X] T650 [US8] Update project README with Part B section
  - **Agent**: OrchestratorAgent
  - **File**: `phase5/README.md`
  - **Add**: Phase V Part B deployment section

- [X] T651 Final Dapr status verification
  - **Agent**: K8sAgent
  - **Command**: `dapr status -k`
  - **Expected**: All healthy

- [X] T652 Mark requirements checklist complete
  - **Agent**: OrchestratorAgent
  - **File**: `phase5/specs/006-phase5-partb-local-deployment/checklists/deployment-checklist.md`
  - **Action**: Mark all items as checked

**Gate**: Documentation complete and reproducible ✓

---

## Dependencies Graph

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Dapr Install)
    │
    ├──────────────────┐
    ▼                  ▼
Phase 3 (Kafka)   Phase 4 (Helm Extension)
    │                  │
    └────────┬─────────┘
             ▼
     Phase 5 (Dapr Components)
             │
             ▼
     Phase 6 (Deployment)
             │
    ┌────────┼────────┐
    ▼        ▼        ▼
Phase 7  Phase 8   Phase 9
(Kafka)  (Dapr)   (E2E)
    │        │        │
    └────────┼────────┘
             ▼
     Phase 10 (Documentation)
```

---

## Parallel Execution Opportunities

| Tasks | Description | Prerequisite |
|-------|-------------|--------------|
| T609 + T610 | Redpanda deployment + service | T608 |
| T613 + T614 | Backend + Frontend Dapr annotations | T612 |
| T620 + T621 + T622 | All Dapr component templates | T619 |
| T624 + T625 | Backend + Frontend Docker builds | T618 |
| T637 + T638 + T639 + T640 | Dapr building block tests | T636 |

---

## Success Criteria Mapping

| Spec SC | Phase | Tasks | Verification |
|---------|-------|-------|--------------|
| SC-001 (Cluster) | 1-2 | T601-T607 | `dapr status -k` |
| SC-002 (Kafka) | 3, 7 | T608-T611, T631-T635 | `rpk topic consume` |
| SC-003 (Helm) | 4, 6 | T612-T630 | 2/2 containers |
| SC-004 (Events) | 7 | T631-T635 | Events in Kafka |
| SC-005 (Dapr) | 8 | T636-T640 | All blocks pass |
| SC-006 (App) | 9 | T641-T645 | Full app works |
| SC-007 (Docs) | 10 | T646-T652 | Docs complete |

---

## Execution Notes

1. **Sequential Execution**: Execute tasks T601-T652 in order
2. **Wait for Confirmation**: After each task, confirm completion before proceeding
3. **Error Handling**: If any task fails, debug and retry before continuing
4. **Agent Assignment**: Use specified agent type for each task
5. **AI-Assisted**: All kubectl/helm commands via kubectl-ai or kagent

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-02-04 | Initial task breakdown |
