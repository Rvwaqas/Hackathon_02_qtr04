# Research: Phase V Part B - Local Minikube + Dapr + Kafka

**Feature ID**: 006-phase5-partb-local-deployment
**Created**: 2026-02-04

---

## 1. Kafka Broker Selection

### Decision: Redpanda (Single Container)

**Rationale**:
- No Zookeeper dependency (Redpanda is self-contained)
- Single container deployment (simpler than Strimzi operator)
- Kafka-compatible API (works with Dapr pubsub.kafka)
- Fast startup time (~30 seconds vs minutes for Strimzi)
- Lower resource footprint (512MB-1GB vs 2GB+ for Strimzi)

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Redpanda** | Simple, fast, no Zookeeper | Less production-like | ✓ SELECTED |
| Strimzi Operator | Production-like, K8s-native | Complex, more resources | For learning only |
| Confluent Platform | Full ecosystem | Heavy, licensing | Over-engineered |

**References**:
- [Redpanda Kubernetes Quickstart](https://docs.redpanda.com/current/deploy/deployment-option/self-hosted/kubernetes/)
- [Dapr Kafka Pub/Sub](https://docs.dapr.io/reference/components-reference/supported-pubsub/setup-apache-kafka/)

---

## 2. Dapr Installation Method

### Decision: `dapr init -k --wait`

**Rationale**:
- Official Dapr CLI method for Kubernetes
- Automatic sidecar injector deployment
- Proper namespace setup (dapr-system)
- `--wait` ensures components ready before continuing

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **dapr init -k** | Official, simple | Requires Dapr CLI | ✓ SELECTED |
| Helm chart (dapr/dapr) | More control | More configuration | Not needed |
| Manual YAML | Full control | Error-prone, complex | Not recommended |

**References**:
- [Dapr Kubernetes Setup](https://docs.dapr.io/operations/hosting/kubernetes/kubernetes-deploy/)

---

## 3. Dapr Sidecar Injection

### Decision: Helm Annotations

**Rationale**:
- Helm-native approach (values-driven)
- Automatic injection by Dapr operator
- Clean separation of concerns
- Easy to enable/disable per deployment

**Required Annotations**:
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "<service-name>"
  dapr.io/app-port: "<port>"
  dapr.io/log-level: "info"
  dapr.io/enable-api-logging: "true"
```

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Helm annotations** | Clean, reusable | Requires annotation on each deployment | ✓ SELECTED |
| dapr run wrapper | Works locally | Not K8s-native | Local dev only |
| Manual sidecar spec | Full control | Verbose, error-prone | Not recommended |

---

## 4. Topic Creation Strategy

### Decision: Dapr Auto-Create

**Rationale**:
- Dapr pubsub.kafka supports auto-creation
- Topics created on first publish
- Less manual setup required
- Consistent with fire-and-forget pattern

**Configuration**:
```yaml
# In pubsub component
metadata:
  - name: initialOffset
    value: "newest"  # Only receive new messages
```

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **Dapr auto-create** | Simple, automatic | Less control over partitions | ✓ SELECTED |
| Init container | Explicit control | More complexity | For production |
| Manual rpk commands | Full control | Manual step | For debugging |

---

## 5. State Store Configuration

### Decision: Dapr state.postgresql (Neon)

**Rationale**:
- Reuse existing Neon PostgreSQL connection
- No additional infrastructure (vs Redis)
- Consistent with application data layer
- Dapr state store for caching only (not main data)

**Use Cases**:
- Conversation session caching
- Temporary state during workflows
- NOT for task data (that goes to main DB tables)

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **state.postgresql** | Consistent, no new infra | Slightly slower than Redis | ✓ SELECTED |
| state.redis | Fast, K/V optimized | Additional pod required | Overkill |
| state.mongodb | Document-friendly | Not needed | Wrong fit |

---

## 6. Secrets Management

### Decision: Kubernetes Secrets + Dapr secretstore

**Rationale**:
- Native Kubernetes approach
- Dapr provides abstraction layer
- No external dependencies (Vault, etc.)
- Sufficient for local development

**Secrets Required**:

| Secret | Key | Source |
|--------|-----|--------|
| db-secrets | connection-string | Neon PostgreSQL URL |
| api-secrets | cohere-api-key | Cohere API |
| api-secrets | gemini-api-key | Google Gemini |
| api-secrets | better-auth-secret | Auth secret |

**Alternatives Considered**:

| Option | Pros | Cons | Decision |
|--------|------|------|----------|
| **K8s Secrets** | Simple, built-in | Base64 only | ✓ SELECTED |
| Sealed Secrets | Encrypted | Requires controller | For production |
| Vault | Full security | Heavy | Overkill for local |

---

## 7. Resource Limits

### Decision: Conservative Limits for Minikube

**Rationale**:
- Minikube has limited resources (4GB total)
- Must fit: Dapr system + Redpanda + 2 app pods
- Conservative limits ensure startup

**Recommended Limits**:

| Component | Memory Limit | CPU Limit |
|-----------|--------------|-----------|
| Backend | 512Mi | 500m |
| Frontend | 256Mi | 250m |
| Redpanda | 1Gi | 1000m |
| Dapr Sidecar | 128Mi (each) | 100m |

**Total**: ~2.5GB (leaves headroom for Dapr system)

---

## 8. Best Practices Applied

### 8.1 Dapr Best Practices

- Use scopes to limit component access
- Enable API logging for debugging
- Use secretKeyRef for sensitive values
- Set appropriate log levels (info for dev)

### 8.2 Kafka/Redpanda Best Practices

- Use ClusterIP service (internal only)
- Set consumerGroup for proper offset tracking
- Use `initialOffset: newest` for new deployments

### 8.3 Helm Best Practices

- Use values files for environment-specific config
- Template all Dapr annotations
- Use helpers for consistent naming

---

## 9. Open Questions Resolved

| Question | Resolution |
|----------|------------|
| Which Kafka broker? | Redpanda (simplicity) |
| How to inject sidecars? | Helm annotations |
| Topic creation method? | Dapr auto-create |
| State store backend? | PostgreSQL (Neon) |
| Secret management? | K8s Secrets + Dapr |
| Resource limits? | Conservative for Minikube |

---

## 10. References

- [Dapr Documentation](https://docs.dapr.io)
- [Redpanda Documentation](https://docs.redpanda.com)
- [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)
- [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/)
- [CloudEvents Specification](https://cloudevents.io/)
