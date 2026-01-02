# Implementation Plan: Console Todo App - Intermediate Level

**Feature Branch**: `002-todo-intermediate`
**Created**: 2025-12-31
**Status**: Draft
**Input**: Spec 002-todo-intermediate

## Technical Context

### Existing Foundation (From Basic Level)
- **Implementation**: `phase1/src/task_manager.py` (141 lines) + `phase1/src/main.py` (244 lines)
- **Architecture**: 2-component design (UI layer + business logic layer)
- **Storage**: In-memory list of dictionaries
- **Current Task Schema**:
  ```python
  task = {
      "id": int,
      "title": str,
      "description": str,
      "completed": bool,
      "created_at": str (ISO format)
  }
  ```

### Extension Approach
- **Strategy**: Enhance existing files (NOT create new ones)
- **Backward Compatibility**: Existing tasks default to `priority="none"`, `tags=[]`
- **New Fields**:
  ```python
  task = {
      # ... existing fields ...
      "priority": str,  # "high" | "medium" | "low" | "none"
      "tags": list[str]  # 0-5 lowercase alphanumeric strings
  }
  ```

### Technology Stack
- **Language**: Python 3.13+ (unchanged)
- **Build Tool**: UV (unchanged)
- **Dependencies**: Zero external dependencies (stdlib only)
- **Platform**: Cross-platform (Windows WSL 2, Linux, macOS)

## Constitution Check

### Compliance Review

**✅ Spec-First Development**
- Implementation plan follows approved spec 002-todo-intermediate
- All requirements documented before code changes
- User stories prioritized (P1-P4)

**✅ AI-Native Architecture**
- All code generation performed by Claude Code
- Human provides requirements, reviews outputs

**✅ Code Quality Standards**
- Type hints required on all new methods
- Async/await: N/A (Phase I uses synchronous I/O)
- Error handling: Validation in CLI layer, None returns in business logic
- Zero hardcoded credentials: N/A (no external services)

**✅ Progressive Enhancement**
- Extends Basic Level without breaking existing functionality
- Backward compatible: existing tasks work with default values
- No data migration needed (in-memory storage)

**✅ Technology Constraints**
- Python 3.13+ with UV: ✅
- Manual code writing prohibited: ✅ (Claude Code generates all code)

### Deviations
None. Intermediate level fully complies with constitution.

## Project Structure

### Files to Modify
```
phase1/
├── src/
│   ├── task_manager.py   # ADD: priority/tag methods, search, filter, sort
│   └── main.py           # ADD: 5 new menu options (6-10), 5 new flow functions
├── specs/
│   └── 002-todo-intermediate/
│       ├── spec.md       # ✅ Created
│       ├── plan.md       # 📝 This file
│       └── tasks.md      # ⏳ Next step
└── README.md             # UPDATE: Document new features

```

### No New Files
- Extend existing `task_manager.py` and `main.py`
- Update existing `README.md` with new feature descriptions

## Design Decisions

### Decision 1: Priority Storage Format

**Options Considered**:
1. **String values** ("high", "medium", "low", "none")
2. Enum class (Priority.HIGH, Priority.MEDIUM, etc.)
3. Integer codes (3=high, 2=medium, 1=low, 0=none)

**Trade-offs**:
- **String**: Human-readable, simple validation, flexible
- **Enum**: Type-safe, prevents typos, requires import
- **Integer**: Efficient sorting, but less readable

**Decision**: Use **string values** with validation

**Rationale**:
- Simplicity: No additional imports, matches Python 3.13+ style
- Readability: Easy to debug and understand in CLI output
- Validation: Simple `if priority not in ["high", "medium", "low", "none"]` check
- Sorting: Map to integers only during sort operation

**Implementation**:
```python
def set_priority(self, task_id: int, priority: str) -> Optional[dict]:
    """Set task priority (high/medium/low/none)."""
    valid_priorities = ["high", "medium", "low", "none"]
    if priority.lower() not in valid_priorities:
        return None
    task = self.get_task(task_id)
    if task:
        task["priority"] = priority.lower()
        return task
    return None
```

---

### Decision 2: Tag Storage Format

**Options Considered**:
1. **List of strings** (preserves order, allows duplicates)
2. Set of strings (no duplicates, no order)
3. Comma-separated string ("work,urgent,home")

**Trade-offs**:
- **List**: Ordered, JSON-serializable, allows duplicates
- **Set**: No duplicates, but not JSON-serializable (Phase II issue)
- **String**: Simple, but requires parsing for every operation

**Decision**: Use **list of strings** with duplicate prevention

**Rationale**:
- Forward compatibility: Phase II will persist to JSON/PostgreSQL
- Duplicate prevention: Check before adding (manual deduplication)
- Order preservation: Tags display in order added
- Simplicity: No additional parsing logic

**Implementation**:
```python
def add_tags(self, task_id: int, new_tags: list[str]) -> Optional[dict]:
    """Add tags to task (max 5 total, alphanumeric, 1-20 chars)."""
    task = self.get_task(task_id)
    if not task:
        return None

    # Normalize and validate
    normalized = []
    for tag in new_tags:
        tag_lower = tag.strip().lower()
        if not tag_lower.isalnum() or len(tag_lower) > 20:
            continue  # Skip invalid
        if tag_lower not in task["tags"]:  # Prevent duplicates
            normalized.append(tag_lower)

    # Check total limit
    if len(task["tags"]) + len(normalized) > 5:
        return None

    task["tags"].extend(normalized)
    return task
```

---

### Decision 3: Search Algorithm

**Options Considered**:
1. **Substring matching** (case-insensitive, simple)
2. Regex pattern matching (flexible, complex)
3. Full-text search with stemming (advanced, requires library)

**Trade-offs**:
- **Substring**: Fast, simple, good enough for small datasets
- **Regex**: Powerful but overkill, security risk (user input)
- **Full-text**: Best results, but violates zero-dependency constraint

**Decision**: Use **case-insensitive substring matching**

**Rationale**:
- Simplicity: `keyword.lower() in title.lower() or keyword.lower() in description.lower()`
- Performance: O(n) linear search acceptable for in-memory storage
- Zero dependencies: No external libraries
- Security: No regex injection risk

**Implementation**:
```python
def search_tasks(self, keyword: str) -> list[dict]:
    """Search tasks by keyword in title or description (case-insensitive)."""
    if not keyword.strip():
        return self.get_all_tasks()  # Empty keyword = all tasks

    keyword_lower = keyword.strip().lower()
    matches = []
    for task in self.tasks:
        if keyword_lower in task["title"].lower() or keyword_lower in task["description"].lower():
            matches.append(task)

    return sorted(matches, key=lambda t: t["created_at"], reverse=True)
```

---

### Decision 4: Filter Combination Logic

**Options Considered**:
1. **AND logic** (status + priority + tag all must match)
2. OR logic (any filter matches)
3. Configurable (user chooses AND/OR)

**Trade-offs**:
- **AND**: Narrows results, more specific, intuitive for most users
- **OR**: Broader results, more flexible
- **Configurable**: Most powerful, but complex UI in CLI

**Decision**: Use **AND logic** (all filters must match)

**Rationale**:
- User expectation: "Show me high-priority pending tasks" means both must be true
- Spec requirement: FR-025 explicitly states "AND logic"
- Simplicity: Single filter method with optional parameters

**Implementation**:
```python
def filter_tasks(
    self,
    status: Optional[str] = None,  # "all" | "pending" | "completed"
    priority: Optional[str] = None,  # "high" | "medium" | "low" | "none"
    tag: Optional[str] = None  # Specific tag name
) -> list[dict]:
    """Filter tasks by status, priority, and/or tag (AND logic)."""
    results = self.tasks[:]

    # Filter by status
    if status and status != "all":
        results = [t for t in results if
                   (status == "completed" and t["completed"]) or
                   (status == "pending" and not t["completed"])]

    # Filter by priority
    if priority:
        results = [t for t in results if t["priority"] == priority]

    # Filter by tag
    if tag:
        results = [t for t in results if tag.lower() in t["tags"]]

    return sorted(results, key=lambda t: t["created_at"], reverse=True)
```

---

### Decision 5: Sort Implementation

**Options Considered**:
1. **In-place sorting** (modify self.tasks list)
2. Return sorted copy (preserve original order)
3. Store last sort preference (stateful)

**Trade-offs**:
- **In-place**: Fast, but destroys original creation order
- **Sorted copy**: Safe, but requires re-sorting on every view
- **Stateful**: Remembers preference, but adds complexity

**Decision**: Use **sorted copy** (view-time sorting)

**Rationale**:
- Preservation: Original creation order remains in self.tasks
- Flexibility: Users can change sort on every view
- Simplicity: No state to manage, no side effects
- Performance: Acceptable for in-memory storage (O(n log n))

**Implementation**:
```python
def sort_tasks(self, sort_by: str, reverse: bool = False) -> list[dict]:
    """Sort tasks by specified criteria.

    Args:
        sort_by: "created" | "title" | "priority" | "status"
        reverse: True for descending, False for ascending

    Returns:
        Sorted list of tasks
    """
    if sort_by == "created":
        return sorted(self.tasks, key=lambda t: t["created_at"], reverse=reverse)
    elif sort_by == "title":
        return sorted(self.tasks, key=lambda t: t["title"].lower(), reverse=reverse)
    elif sort_by == "priority":
        priority_map = {"high": 3, "medium": 2, "low": 1, "none": 0}
        return sorted(self.tasks, key=lambda t: priority_map[t["priority"]], reverse=reverse)
    elif sort_by == "status":
        return sorted(self.tasks, key=lambda t: t["completed"], reverse=reverse)
    else:
        return self.get_all_tasks()  # Default: newest first
```

## Implementation Phases

### Phase 0: Data Model Extension (Foundation)
**Blocking**: All subsequent phases depend on this

**Changes to `task_manager.py`**:
- Modify `add_task()` method to include default `priority="none"`, `tags=[]`
- Update task creation to:
  ```python
  task = {
      "id": self._generate_id(),
      "title": title.strip(),
      "description": description.strip(),
      "completed": False,
      "priority": "none",  # NEW
      "tags": [],  # NEW
      "created_at": datetime.now().isoformat()
  }
  ```

**Validation**: Create task, verify it has priority and tags fields

---

### Phase 1: Priority Management (User Story 2 - P1)
**Goal**: Users can assign and view priority levels

**Changes to `task_manager.py`**:
- Add `set_priority(task_id: int, priority: str) -> Optional[dict]`
- Validation: Check priority in ["high", "medium", "low", "none"]

**Changes to `main.py`**:
- Update `display_menu()` to add option "6. Set Priority"
- Update `get_user_choice()` to accept "1-11"
- Add `set_priority_flow(manager: TaskManager) -> None`
  - Prompt for task ID and priority level
  - Validate input
  - Display confirmation
- Update `view_tasks_flow()` to show priority indicators:
  ```python
  priority_indicator = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
  indicator = f"{priority_indicator[task['priority']]} "
  print(f"{indicator}{checkbox} {task['id']}. {task['title']}...")
  ```

**Validation**: Create task, set priority to "high", view list (verify [H] indicator)

---

### Phase 2: Tag Management (User Story 2 - P1)
**Goal**: Users can add/remove tags and view them

**Changes to `task_manager.py`**:
- Add `add_tags(task_id: int, new_tags: list[str]) -> Optional[dict]`
  - Validate: alphanumeric, 1-20 chars, max 5 total
- Add `remove_tags(task_id: int, tags_to_remove: list[str]) -> Optional[dict]`

**Changes to `main.py`**:
- Update `display_menu()` to add options "7. Manage Tags"
- Add `manage_tags_flow(manager: TaskManager) -> None`
  - Prompt for task ID
  - Show current tags
  - Ask: "1. Add tags" or "2. Remove tags"
  - Prompt for comma-separated tags
  - Display confirmation
- Update `view_tasks_flow()` to show tags:
  ```python
  if task["tags"]:
      tags_display = " ".join(f"#{tag}" for tag in task["tags"])
      print(f"   {tags_display}")
  ```

**Validation**: Create task, add tags "work,urgent", view list (verify #work #urgent display)

---

### Phase 3: Search Tasks (User Story 3 - P2)
**Goal**: Users can search for tasks by keyword

**Changes to `task_manager.py`**:
- Add `search_tasks(keyword: str) -> list[dict]`
  - Case-insensitive substring matching
  - Search in title and description
  - Return sorted by created_at (newest first)

**Changes to `main.py`**:
- Update `display_menu()` to add option "8. Search Tasks"
- Add `search_tasks_flow(manager: TaskManager) -> None`
  - Prompt for search keyword
  - Call `manager.search_tasks(keyword)`
  - Display count: "Found X tasks:"
  - Display results using modified `view_tasks_flow()` logic
  - If empty: "No tasks found matching '<keyword>'"

**Validation**: Create tasks with different titles, search for keyword, verify only matches appear

---

### Phase 4: Filter Tasks (User Story 4 - P3)
**Goal**: Users can filter by status, priority, or tag

**Changes to `task_manager.py`**:
- Add `filter_tasks(status: Optional[str], priority: Optional[str], tag: Optional[str]) -> list[dict]`
  - AND logic: all specified filters must match
  - Return sorted by created_at

**Changes to `main.py`**:
- Update `display_menu()` to add option "9. Filter Tasks"
- Add `filter_tasks_flow(manager: TaskManager) -> None`
  - Ask: "Filter by: 1. Status, 2. Priority, 3. Tag, 4. Combined"
  - Prompt for filter values based on choice
  - Call `manager.filter_tasks()`
  - Display count: "Showing X of Y tasks"
  - Display results
  - If empty: "No tasks found matching filters"

**Validation**: Create tasks with different priorities, filter by "high" priority, verify only high-priority tasks appear

---

### Phase 5: Sort Tasks (User Story 5 - P4)
**Goal**: Users can sort by created/title/priority/status

**Changes to `task_manager.py`**:
- Add `sort_tasks(sort_by: str, reverse: bool) -> list[dict]`
  - Support: "created", "title", "priority", "status"
  - Priority sorting: map to integers (high=3, medium=2, low=1, none=0)

**Changes to `main.py`**:
- Update `display_menu()` to add option "10. Sort Tasks"
- Add `sort_tasks_flow(manager: TaskManager) -> None`
  - Ask: "Sort by: 1. Created (newest), 2. Created (oldest), 3. Title (A-Z), 4. Title (Z-A), 5. Priority (high→low), 6. Priority (low→high), 7. Status"
  - Call `manager.sort_tasks()`
  - Display sort criteria in header: "Sorted by: Priority (high → low)"
  - Display results

**Validation**: Create tasks with different priorities, sort by priority, verify order is high → medium → low → none

---

### Phase 6: Menu Integration
**Goal**: Update main menu to show all 11 options

**Changes to `main.py`**:
- Update `display_menu()`:
  ```python
  print("\n=== Todo App ===")
  print("1. Add Task")
  print("2. View All Tasks")
  print("3. Update Task")
  print("4. Delete Task")
  print("5. Mark Complete/Incomplete")
  print("6. Set Priority")
  print("7. Manage Tags")
  print("8. Search Tasks")
  print("9. Filter Tasks")
  print("10. Sort Tasks")
  print("11. Exit")
  ```
- Update `get_user_choice()` to validate "1-11"
- Update `main()` event loop to route choices 6-11

**Validation**: Run app, verify menu shows all options, test each new option

---

### Phase 7: Polish & Documentation
**Goal**: Final validation and README updates

**Changes to `README.md`**:
- Update feature list to include priorities, tags, search, filter, sort
- Add examples for new features
- Update success criteria

**Validation Tasks**:
- Test all User Story 2 acceptance scenarios (priorities & tags)
- Test all User Story 3 acceptance scenarios (search)
- Test all User Story 4 acceptance scenarios (filter)
- Test all User Story 5 acceptance scenarios (sort)
- Test all edge cases from spec (6 tags, invalid priority, empty search, etc.)
- Verify full demo workflow completes in <90 seconds

## Testing Strategy

### Manual Validation (Phase I approach)
No automated tests - manual validation against acceptance scenarios.

**Test Cases to Verify**:
1. **Priorities**: Create task, set priority to "high", verify [H] indicator
2. **Tags**: Add tags "work,urgent", verify #work #urgent display
3. **Tag Limits**: Try to add 6 tags, verify error "Maximum 5 tags allowed"
4. **Search**: Search for "groceries", verify only matching tasks appear
5. **Filter**: Filter by "high" priority + "pending" status, verify combined logic
6. **Sort**: Sort by priority, verify order is high → medium → low → none
7. **Edge Cases**: Empty search keyword, invalid priority, tag with special characters

### Acceptance Criteria Validation
- [ ] User Story 2: All 5 acceptance scenarios pass
- [ ] User Story 3: All 3 acceptance scenarios pass
- [ ] User Story 4: All 4 acceptance scenarios pass
- [ ] User Story 5: All 4 acceptance scenarios pass
- [ ] All 6 edge cases handled correctly

## Dependencies

### Requires
- **Spec 001-console-todo-app**: Basic implementation must be complete ✅
- **Files**: `phase1/src/task_manager.py`, `phase1/src/main.py` must exist ✅

### Blocks
None - this is an iterative enhancement, not a dependency for other features

### Related
- **Phase II**: Will add persistence to both basic and intermediate features
- **Phase III**: AI chatbot will interact with these enhanced tasks

## Risks and Mitigations

### Risk 1: Breaking Existing Functionality
**Probability**: Medium
**Impact**: High
**Mitigation**:
- Test all existing features (US1-US5 from Basic Level) after each phase
- Use default values (priority="none", tags=[]) to ensure backward compatibility

### Risk 2: Tag Validation Complexity
**Probability**: Low
**Impact**: Low
**Mitigation**:
- Use simple alphanumeric check: `tag.isalnum()`
- Skip invalid tags silently rather than failing entire operation

### Risk 3: Sort Performance Degradation
**Probability**: Low
**Impact**: Low
**Mitigation**:
- SC-022 requires 100+ tasks to work without degradation
- Python's built-in `sorted()` is O(n log n), acceptable for in-memory storage
- Test with 100+ tasks during validation

## Success Criteria

### Implementation Complete When
- [ ] All 5 user stories (US1-US5) implemented and tested
- [ ] All 15 new functional requirements (FR-016 to FR-030) met
- [ ] All 12 new success criteria (SC-011 to SC-022) verified
- [ ] All edge cases from spec handled correctly
- [ ] README.md updated with new features
- [ ] Full demo workflow completes in <90 seconds

### Code Quality Checklist
- [ ] Type hints on all new methods
- [ ] Docstrings on all new functions
- [ ] Input validation in CLI layer
- [ ] Error handling for invalid inputs
- [ ] ASCII-only output (no Unicode issues)
- [ ] PEP 8 compliant

## Next Steps

1. **Create tasks.md**: Break down this plan into specific tasks (T059-T100+)
2. **Run `/sp.implement`**: Execute all tasks sequentially
3. **Manual validation**: Test against all acceptance scenarios
4. **Update README.md**: Document new features with examples
5. **Create demo**: Show all intermediate features in <90 seconds
6. **Commit**: `feat: add priorities, tags, search, filter, sort to Phase I app`

---

**Plan Version**: 1.0
**Estimated Complexity**: Medium (extends existing code, no new files)
**Estimated Tasks**: ~45 tasks across 7 phases
**Estimated Time**: ~4 hours (single developer, sequential implementation)
