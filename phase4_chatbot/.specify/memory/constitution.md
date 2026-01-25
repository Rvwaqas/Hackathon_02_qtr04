# Phase IV: Local Kubernetes Deployment Constitution

<!--
SYNC IMPACT REPORT
Version Change: 1.0.0 → 2.0.0 (MAJOR: Phase transition from AI Chatbot to K8s Deployment)

Modified Principles:
  1. "Strictly Spec-Driven Development" → retained, expanded for infrastructure
  2. "Seamless Backend Integration" → replaced with "AI-Assisted Operations Only"
  3. "User Data Isolation & Security" → replaced with "Backward Compatibility"
  4. "Stateless Server Architecture" → replaced with "Reusable Blueprints"
  5. "Tech Stack Standardization" → replaced with "Demonstrable AIOps"
  NEW: "Tech Stack Standardization (Phase IV)" added as 6th principle

New Sections:
  - Docker Images Standards
  - Helm Chart Standards
  - Kubernetes Resources Standards
  - AI-Assisted Operations Standards
  - Non-Negotiables section (explicit hard constraints)
  - Bonus Alignment section (hackathon criteria)

Removed Sections:
  - Database Extensions (retained via Backward Compatibility)
  - MCP Tools (Phase III specific)
  - Agent Behavior Standards (replaced with AIOps standards)

Templates requiring review:
  ✅ .specify/templates/plan-template.md (Constitution Check section generic, no update needed)
  ✅ .specify/templates/spec-template.md (User Stories structure generic, no update needed)
  ✅ .specify/templates/tasks-template.md (Phase structure generic, no update needed)

Deferred Items: None
-->

## Core Principles

### I. Strictly Spec-Driven Development

No infrastructure change without direct reference to a specification file or task in `/specs/`. All containerization, Helm chart generation, and Kubernetes operations must be generated via AI agents using approved specifications. Every deployment artifact must have a corresponding spec document that precedes implementation. This ensures traceability, reduces manual errors, and keeps infrastructure aligned with application requirements.

### II. AI-Assisted Operations Only (NON-NEGOTIABLE)

No manual coding or manual `kubectl`/`helm` commands are allowed outside the AI-assisted flow. All containerization must use Gordon AI (Docker's AI assistant). All Helm chart generation and Kubernetes operations must use kubectl-ai and/or kagent. Manual fallback is permitted ONLY when Gordon is unavailable, and such instances MUST be documented with justification.

### III. Backward Compatibility

The deployed application MUST retain all Phase III functionality without regression. This includes:
- Cohere-powered AI chatbot working end-to-end
- Full task management (CRUD operations via dashboard and natural language)
- User isolation (multi-user data separation)
- Stateless chat endpoint with database-backed conversation persistence
- Better Auth + JWT authentication flow

Breaking Phase III functionality is a deployment failure regardless of infrastructure success.

### IV. Reusable Blueprints

All infrastructure artifacts MUST be designed for reusability in future phases and projects. Create blueprints and patterns that can be adapted for:
- Different application types (not just this chatbot)
- Different deployment targets (Phase V: DigitalOcean)
- Different team members (clear documentation)

Avoid one-off configurations; prefer parameterized, templated solutions.

### V. Demonstrable AIOps

Heavy use of Gordon, kubectl-ai, and kagent MUST be visible in both process and documentation. Every deployment step should demonstrate AI-assisted operations through:
- Gordon prompts captured in documentation or logs
- kubectl-ai commands for deployment, scaling, and debugging
- kagent commands for health analysis and optimization
- All agent roles (DockerAgent, HelmAgent, K8sAgent, BlueprintAgent) visible in process

This is a hackathon requirement: judges must see clear evidence of AIOps usage.

### VI. Tech Stack Standardization (Phase IV)

The following technologies are mandatory for Phase IV deployment:
- **Containerization**: Docker Desktop with Gordon AI enabled
- **Orchestration**: Minikube (local Kubernetes cluster)
- **Packaging**: Helm Charts (single chart for frontend + backend)
- **AIOps Tools**: Gordon (Docker AI), kubectl-ai, kagent
- **Application Stack** (from Phase III): Next.js 16+, FastAPI, Cohere API, Neon PostgreSQL

## Key Standards

### Docker Images

- **Separate Images**: Frontend (Next.js standalone) and Backend (FastAPI + Cohere agent) MUST be separate Docker images
- **Multi-Stage Builds**: Mandatory for both images to optimize size
- **Size Targets**: Frontend < 100MB, Backend < 200MB
- **Local Testing**: Images MUST run successfully with `docker run` before Kubernetes deployment
- **Gordon Usage**: Dockerfile generation/optimization MUST use Gordon AI (fallback documented if unavailable)

### Helm Chart

- **Single Chart**: One Helm chart managing both frontend and backend deployments/services
- **ConfigMap**: Non-sensitive configuration values
- **Secrets**: BETTER_AUTH_SECRET, COHERE_API_KEY, DATABASE_URL, NEXT_PUBLIC_OPENAI_DOMAIN_KEY
- **Template Generation**: Templates MUST be generated primarily via kubectl-ai / kagent
- **Validation**: Chart MUST pass `helm lint` and `helm install --dry-run` before deployment

### Kubernetes Resources

- **Replicas**: 1 replica each by default (scalable via AI commands)
- **Database**: External Neon PostgreSQL (no local DB pod required)
- **Access**: Local access via `minikube service --url` or `kubectl port-forward`
- **Resources**: Limits suitable for laptop (no over-allocation causing OOM)
- **No Ingress**: Ingress controller not required for local deployment

### AI-Assisted Operations

| Tool | Required Usage |
|------|----------------|
| **Gordon** | Dockerfile generation, image optimization, security suggestions |
| **kubectl-ai** | Deployment creation, scaling, debugging, resource management |
| **kagent** | Cluster health analysis, resource optimization, troubleshooting |

## Constraints

### Infrastructure Constraints
- Local deployment only (Minikube on Docker Desktop)
- External Neon DB connection via Kubernetes Secret
- No Ingress controller required (use `minikube service --url`)
- No persistent volumes needed (stateless app + external DB)
- Resource limits suitable for laptop (no over-allocation)

### Phase Constraints
- No cloud providers (DigitalOcean is Phase V only)
- Must preserve all Phase III functionality
- Gordon fallback allowed only if unavailable and documented

### Process Constraints
- Every action must be traceable to a spec/plan/task
- No manual docker build/kubectl/helm without AI assistance
- Secrets never hardcoded; use Helm secrets or environment injection

## Success Criteria

### Docker Phase
- [ ] Both frontend and backend successfully containerized
- [ ] Images run locally with `docker run` and respond to health checks
- [ ] Image sizes meet targets (frontend < 100MB, backend < 200MB)
- [ ] Gordon AI used for Dockerfile generation (or fallback documented)

### Helm Phase
- [ ] Complete Helm chart created with all resources
- [ ] Chart passes `helm lint` without errors
- [ ] Chart passes `helm install --dry-run` successfully
- [ ] kubectl-ai / kagent used for template generation

### Kubernetes Phase
- [ ] Application successfully deployed to Minikube via `helm install`
- [ ] Both services running and accessible locally
- [ ] Health endpoints return 200 OK

### Functionality Phase
- [ ] Login via Better Auth works
- [ ] Task CRUD via dashboard works
- [ ] Natural language task management via chatbot works (Cohere agent)
- [ ] Conversation persists after pod restart

### Documentation Phase
- [ ] README includes exact deployment steps
- [ ] AI commands used are documented
- [ ] All agent roles (DockerAgent, HelmAgent, K8sAgent, BlueprintAgent) visible

## Non-Negotiables

These are absolute requirements with no exceptions:

1. **Never** use manual `docker build`/`kubectl`/`helm` without AI assistance
2. **Never** hardcode secrets in code, values files, or documentation
3. **Never** bypass spec-driven process; every action traceable to plan/tasks
4. **Never** break Phase III functionality (chatbot must work in deployed app)
5. **Always** use Gordon for Docker operations (screenshot/log proof if needed)
6. **Always** demonstrate chatbot working inside Minikube-deployed app for final demo

## Bonus Alignment

These align with hackathon bonus criteria:

- **Multi-Agent Orchestration**: Clear demonstration of BlueprintAgent coordinating DockerAgent → HelmAgent → K8sAgent
- **AIOps Evidence**: Extensive use of kubectl-ai and kagent commands captured in documentation
- **Optimization**: Resource usage tuning and troubleshooting examples using AI tools
- **Reusability**: Helm blueprint designed for reuse in Phase V and future projects

## Governance

**Amendment Procedure**:
- Constitution supersedes all other practices and specifications.
- Amendments require written justification (PR description or issue) and explicit approval from project lead.
- Each amendment must update the `LAST_AMENDED_DATE` and increment `CONSTITUTION_VERSION` according to semantic versioning.
- Breaking changes (principle removals or redefinitions) require MAJOR version bump; new principles or sections require MINOR; clarifications require PATCH.

**Compliance & Review**:
- All PRs and code reviews must verify compliance with core principles (especially AI-Assisted Operations, Backward Compatibility, and Spec-Driven Development).
- Specification documents must explicitly reference principles they enforce or violate.
- Deployment artifacts must reflect constitution-mandated requirements (e.g., AIOps usage, image size targets).

**Runtime Guidance**:
- See `CLAUDE.md` in project root for development workflow, tool usage, and coding standards.
- See `.claude/agents/` for specialized agent definitions (DockerAgent, HelmAgent, K8sAgent, BlueprintAgent).
- See `docs/` for API contracts, deployment guides, and architecture decisions.

**Version**: 2.0.0 | **Ratified**: 2026-01-15 | **Last Amended**: 2026-01-22
