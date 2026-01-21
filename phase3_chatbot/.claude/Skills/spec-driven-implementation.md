# Skill: Spec-Driven Implementation

## Purpose
Read specification files (specify.md, plan.md, tasks.md) and generate implementation code that strictly follows the Spec-Driven Development (SDD) workflow.

## Core Principles
1. **Never code without a task** - Every line of code must map to a task ID
2. **Never invent features** - Only implement what's in the specification
3. **Never skip planning** - Specify → Plan → Tasks → Implement (no shortcuts)
4. **Always reference back** - Link code to specific sections in specs

## Workflow

### Step 1: Read Constitution
```markdown
Before ANY implementation, read:
- constitution.md (project principles, constraints, tech stack)
```

### Step 2: Understand the Specify (WHAT)
```markdown
Read: specs/phaseX/specify.md
Extract:
- User stories
- Requirements
- Acceptance criteria
- Domain rules
- Business constraints
```

### Step 3: Validate the Plan (HOW)
```markdown
Read: specs/phaseX/plan.md
Verify:
- Component architecture
- API endpoints/interfaces
- Data models
- Service boundaries
- Dependencies
```

### Step 4: Execute Tasks (IMPLEMENT)
```markdown
Read: specs/phaseX/tasks.md
For each task:
1. Check task ID and description
2. Verify preconditions are met
3. Implement ONLY what the task describes
4. Add reference comments in code
5. Mark task as complete
```

## Code Comment Pattern

Every file must include a header:
```python
"""
[Task]: T-001, T-002
[From]: specify.md §2.1, plan.md §3.4
[Purpose]: Implement user authentication endpoint
"""
```

Every function must reference its task:
```python
def create_task(title: str, description: str):
    """
    Create a new task in the database.
    
    [Task]: T-005
    [Spec]: specify.md §3.2 - Task Creation
    """
    pass
```

## Implementation Rules

### DO:
- ✅ Follow the exact architecture in plan.md
- ✅ Implement features exactly as specified
- ✅ Use tech stack from constitution.md
- ✅ Add task references in comments
- ✅ Stop if specification is unclear or missing

### DON'T:
- ❌ Add "nice to have" features not in spec
- ❌ Change tech stack without updating constitution
- ❌ Modify architecture without updating plan
- ❌ Skip tasks or implement them out of order
- ❌ Freestyle code without task reference

## When to Stop and Ask

Stop implementation if:
1. **Task is ambiguous** - Request clarification in tasks.md
2. **Spec contradicts constitution** - Flag the conflict
3. **Architecture is unclear** - Request update to plan.md
4. **Feature is missing from specify** - Request requirement addition
5. **Dependency is unavailable** - Flag blocked task

## Example Usage

### Bad Implementation (No Spec-Driven)
```python
# ❌ No task reference
def create_task(data):
    # ❌ Added extra validation not in spec
    if len(data['title']) < 3:
        raise ValueError("Title too short")
    
    # ❌ Added caching not in architecture
    cache.set(f"task_{id}", task)
    
    return Task.create(**data)
```

### Good Implementation (Spec-Driven)
```python
"""
[Task]: T-005
[From]: specify.md §3.2, plan.md §4.1
[Purpose]: Create task with title and optional description
"""

def create_task(user_id: str, title: str, description: str = None) -> Task:
    """
    Create a new task for authenticated user.
    
    [Task]: T-005
    [Acceptance Criteria]:
    - Title required (1-200 chars) ✓
    - Description optional (max 1000 chars) ✓
    - Associated with logged-in user ✓
    
    [Spec Reference]: specify.md §3.2
    """
    # Validation per acceptance criteria
    if not title or len(title) > 200:
        raise ValueError("Title must be 1-200 characters")
    
    if description and len(description) > 1000:
        raise ValueError("Description max 1000 characters")
    
    # Implementation per plan.md §4.1
    task = Task(
        user_id=user_id,
        title=title,
        description=description,
        completed=False
    )
    
    return task.save()
```

## Output Format

After implementing each task, provide:
```markdown
### Task T-XXX: [Task Name]
**Status**: ✅ Complete

**Files Modified**:
- `backend/routes/tasks.py` (created)
- `backend/models.py` (updated Task model)

**Spec Compliance**:
- ✅ Matches plan.md §4.1 architecture
- ✅ Implements all acceptance criteria from specify.md §3.2
- ✅ Uses tech stack from constitution (FastAPI + SQLModel)

**Next Task**: T-XXX (or "All tasks complete")
```

## Integration with Claude Code

When using this skill:
1. Claude Code loads AGENTS.md
2. AGENTS.md instructs to use this skill
3. Claude reads specs before coding
4. Claude implements with task references
5. Claude reports compliance

## Summary

This skill ensures:
- **Traceability**: Every line of code traces to a requirement
- **Predictability**: Implementation matches specification exactly
- **Quality**: No scope creep or freestyle coding
- **Maintainability**: Future developers understand WHY code exists