# Implementation Plan: [FEATURE_NAME]

**Spec Reference**: `specs/[FEATURE_DIR]/spec.md`
**Created**: [CREATED_DATE]
**Status**: Draft | Approved | In Progress | Complete
**Constitution Check**: Verified against `.specify/memory/constitution.md` v[VERSION]

## Overview

[Brief summary of the implementation approach]

## Architecture Decisions

### Decision 1: [Decision Title]

**Context**: [Why this decision is needed]

**Options Considered**:
1. [Option A] - [Pros/Cons]
2. [Option B] - [Pros/Cons]

**Decision**: [Chosen option]

**Rationale**: [Why this option was selected]

**Constitution Alignment**: [Which principles this supports]

---

## Component Breakdown

### Component 1: [Component Name]

**Purpose**: [What this component does]

**Location**: `[file_path]`

**Dependencies**: [Other components or services]

**Key Interfaces**:
```python
# API signature or interface definition
```

---

## Data Model Changes

### New Tables

```sql
-- Table definition
CREATE TABLE [table_name] (
    id SERIAL PRIMARY KEY,
    ...
);
```

### Schema Migrations

- [ ] Migration script created
- [ ] Rollback script created
- [ ] Tested on development database

---

## API Contracts

### Endpoint: [METHOD] /api/[path]

**Request**:
```json
{
  "field": "value"
}
```

**Response (Success)**:
```json
{
  "success": true,
  "data": {}
}
```

**Response (Error)**:
```json
{
  "success": false,
  "error": "message"
}
```

---

## Implementation Sequence

1. **Phase 1**: [Component/Feature] - [Brief description]
2. **Phase 2**: [Component/Feature] - [Brief description]
3. **Phase 3**: [Component/Feature] - [Brief description]

---

## Risk Analysis

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| [Risk description] | Low/Med/High | Low/Med/High | [Mitigation strategy] |

---

## Testing Strategy

### Unit Tests
- [ ] [Test description]

### Integration Tests
- [ ] [Test description]

### End-to-End Tests
- [ ] [Test description]

---

## Constitution Compliance Checklist

- [ ] P1: Spec reference included
- [ ] P2: Backward compatibility verified
- [ ] P3: User isolation in all queries
- [ ] P4: No in-memory state
- [ ] P5: Cohere API only
- [ ] P6: MCP tools follow spec
- [ ] P7: Conversation persistence implemented
- [ ] P8: JWT auth reused
- [ ] P9: ChatKit integration planned
- [ ] P10: Graceful error handling planned

---

## ADR Suggestions

<!-- If architecturally significant decisions were made, suggest ADRs -->

📋 Architectural decision detected: [brief description]
   Document reasoning and tradeoffs? Run `/sp.adr [decision-title]`
