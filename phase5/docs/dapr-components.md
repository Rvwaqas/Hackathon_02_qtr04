# Dapr Component Configurations

## 1. kafka-pubsub (pubsub.kafka)

Publishes task lifecycle events to Redpanda/Kafka topics.

```yaml
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
  - todo-backend  # Only backend can publish
```

**Usage**: Backend publishes CloudEvents via `POST http://localhost:3500/v1.0/publish/kafka-pubsub/{topic}`

## 2. statestore (state.postgresql)

Uses Neon PostgreSQL for Dapr state management (conversation caching).

```yaml
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
        name: todo-chatbot-secrets
        key: database-url
    - name: tableName
      value: "dapr_state"
scopes:
  - todo-backend
```

**Usage**:
- Save: `POST http://localhost:3500/v1.0/state/statestore`
- Get: `GET http://localhost:3500/v1.0/state/statestore/{key}`

## 3. kubernetes-secrets (secretstores.kubernetes)

Provides access to Kubernetes secrets via Dapr API.

```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: kubernetes-secrets
spec:
  type: secretstores.kubernetes
  version: v1
  metadata: []
```

**Usage**: `GET http://localhost:3500/v1.0/secrets/kubernetes-secrets/{secret-name}`

## 4. Jobs API (Built-in)

Dapr Jobs API is built into the runtime - no component needed.

**Usage**:
- Schedule: `POST http://localhost:3500/v1.0/jobs/{name}`
- List: `GET http://localhost:3500/v1.0/jobs`
- Delete: `DELETE http://localhost:3500/v1.0/jobs/{name}`

## 5. Service Invocation (Built-in)

Direct service-to-service calls via Dapr sidecar.

**Usage**: `GET http://localhost:3500/v1.0/invoke/{app-id}/method/{path}`
