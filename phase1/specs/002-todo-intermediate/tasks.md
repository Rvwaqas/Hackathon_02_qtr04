---
description: "Task list for Console Todo App - Intermediate Level implementation"
---

# Tasks: Console Todo App - Intermediate Level

**Input**: Design documents from `phase1/specs/002-todo-intermediate/`
**Prerequisites**: plan.md (completed), spec.md (completed), Basic Level (001-console-todo-app) fully implemented

**Tests**: No automated tests in Phase I - manual validation only per plan.md.

**Organization**: Tasks are grouped by user story (after Phase 0) to enable independent implementation and testing of each intermediate feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

- **Project root**: `phase1/`
- **Source code**: `phase1/src/`
- **Documentation**: `phase1/` (README.md)

---

## Phase 0: Data Model Extension (Foundation for Intermediate Features)

**Purpose**: Extend task data structure to support priority and tags - MUST be complete before ANY intermediate feature implementation

**⚠️ CRITICAL**: All intermediate features depend on this phase being complete

- [x] T059 Extend add_task() method to include priority and tags fields in phase1/src/task_manager.py
- [x] T060 Set default priority="none" for new tasks in add_task() method
- [x] T061 Set default tags=[] for new tasks in add_task() method
- [x] T062 Verify task dictionary structure includes all 7 fields (id, title, description, completed, priority, tags, created_at)

**Checkpoint**: Data model extended - task creation now includes priority and tags with default values

---

## Phase 1: User Story 2 - Priorities & Tags (Priority: P1) 🎯 High Value

**Goal**: Users can assign priority levels (high/medium/low/none) and tags (0-5 per task) to organize and categorize tasks

**Independent Test**: Create task, set priority to "high", add tags "work,urgent", verify display shows [H] indicator and #work #urgent tags

### Implementation for User Story 2 - Priority Management

- [x] T063 [US2] Implement set_priority(task_id, priority) method in phase1/src/task_manager.py
- [x] T064 [US2] Add priority validation (must be "high", "medium", "low", or "none") in set_priority() method
- [x] T065 [US2] Return None from set_priority() if task not found or priority invalid
- [x] T066 [US2] Add docstring to set_priority() method with type hints

### Implementation for User Story 2 - Tag Management

- [x] T067 [US2] Implement add_tags(task_id, new_tags) method in phase1/src/task_manager.py
- [x] T068 [US2] Add tag validation in add_tags(): alphanumeric only, 1-20 chars each
- [x] T069 [US2] Add tag limit enforcement in add_tags(): max 5 tags total per task
- [x] T070 [US2] Add duplicate prevention in add_tags(): skip tags already in task["tags"]
- [x] T071 [US2] Store all tags as lowercase in add_tags() method
- [x] T072 [US2] Implement remove_tags(task_id, tags_to_remove) method in phase1/src/task_manager.py
- [x] T073 [US2] Add docstrings to add_tags() and remove_tags() methods with type hints

### CLI Integration for User Story 2

- [x] T074 [US2] Implement set_priority_flow(manager) function in phase1/src/main.py
- [x] T075 [US2] Add task ID input prompt in set_priority_flow()
- [x] T076 [US2] Add priority selection prompt in set_priority_flow() (show options: high/medium/low/none)
- [x] T077 [US2] Add error handling for invalid task ID in set_priority_flow()
- [x] T078 [US2] Add error handling for invalid priority value in set_priority_flow()
- [x] T079 [US2] Add success message showing priority indicator in set_priority_flow()
- [x] T080 [US2] Implement manage_tags_flow(manager) function in phase1/src/main.py
- [x] T081 [US2] Add task ID input prompt in manage_tags_flow()
- [x] T082 [US2] Display current tags in manage_tags_flow()
- [x] T083 [US2] Add submenu for add/remove tags choice in manage_tags_flow()
- [x] T084 [US2] Add comma-separated tag input prompt in manage_tags_flow()
- [x] T085 [US2] Add error handling for tag validation failures in manage_tags_flow()
- [x] T086 [US2] Add success message showing updated tags in manage_tags_flow()

### Display Updates for User Story 2

- [x] T087 [US2] Update view_tasks_flow() to display priority indicators ([H], [M], [L]) in phase1/src/main.py
- [x] T088 [US2] Update view_tasks_flow() to display tags with # prefix (e.g., #work #urgent)
- [x] T089 [US2] Format priority indicator before task checkbox in display
- [x] T090 [US2] Format tags after task description in display

### Menu Integration for User Story 2

- [x] T091 [US2] Update display_menu() to add option "6. Set Priority"
- [x] T092 [US2] Update display_menu() to add option "7. Manage Tags"
- [x] T093 [US2] Update get_user_choice() to validate choices "1-11" (Exit becomes option 11)
- [x] T094 [US2] Add route for choice "6" to call set_priority_flow() in main() event loop
- [x] T095 [US2] Add route for choice "7" to call manage_tags_flow() in main() event loop

**Checkpoint**: At this point, User Story 2 should be fully functional - users can set priorities and manage tags

---

## Phase 2: User Story 3 - Search Tasks (Priority: P2)

**Goal**: Users can search for tasks by keyword in title or description (case-insensitive)

**Independent Test**: Create tasks with different titles/descriptions, search for "groceries", verify only matching tasks appear with count message

### Implementation for User Story 3

- [x] T096 [US3] Implement search_tasks(keyword) method in phase1/src/task_manager.py
- [x] T097 [US3] Add case-insensitive substring matching logic in search_tasks()
- [x] T098 [US3] Search both title and description fields in search_tasks()
- [x] T099 [US3] Return empty search keyword as all tasks in search_tasks()
- [x] T100 [US3] Return sorted results (newest first) from search_tasks()
- [x] T101 [US3] Add docstring to search_tasks() method with type hints

### CLI Integration for User Story 3

- [x] T102 [US3] Implement search_tasks_flow(manager) function in phase1/src/main.py
- [x] T103 [US3] Add keyword input prompt in search_tasks_flow()
- [x] T104 [US3] Call manager.search_tasks() with user keyword in search_tasks_flow()
- [x] T105 [US3] Display result count message "Found X tasks matching 'keyword':" in search_tasks_flow()
- [x] T106 [US3] Display search results using existing task display format in search_tasks_flow()
- [x] T107 [US3] Display "No tasks found matching 'keyword'" message for empty results in search_tasks_flow()

### Menu Integration for User Story 3

- [x] T108 [US3] Update display_menu() to add option "8. Search Tasks"
- [x] T109 [US3] Add route for choice "8" to call search_tasks_flow() in main() event loop

**Checkpoint**: At this point, User Stories 2 AND 3 should both work independently

---

## Phase 3: User Story 4 - Filter Tasks (Priority: P3)

**Goal**: Users can filter tasks by status, priority, or tags, with support for combined filters (AND logic)

**Independent Test**: Create tasks with different priorities and statuses, filter by "high priority + pending status", verify only matching tasks appear with count

### Implementation for User Story 4

- [x] T110 [US4] Implement filter_tasks(status, priority, tag) method in phase1/src/task_manager.py
- [x] T111 [US4] Add status filter logic in filter_tasks() (all/pending/completed)
- [x] T112 [US4] Add priority filter logic in filter_tasks() (high/medium/low/none)
- [x] T113 [US4] Add tag filter logic in filter_tasks() (check if tag in task["tags"])
- [x] T114 [US4] Implement AND logic for combined filters in filter_tasks()
- [x] T115 [US4] Return sorted results (newest first) from filter_tasks()
- [x] T116 [US4] Add docstring to filter_tasks() method with type hints and Optional parameters

### CLI Integration for User Story 4

- [x] T117 [US4] Implement filter_tasks_flow(manager) function in phase1/src/main.py
- [x] T118 [US4] Add filter type selection menu in filter_tasks_flow() (1=Status, 2=Priority, 3=Tag, 4=Combined)
- [x] T119 [US4] Add status selection prompt in filter_tasks_flow() (all/pending/completed)
- [x] T120 [US4] Add priority selection prompt in filter_tasks_flow() (high/medium/low/none)
- [x] T121 [US4] Add tag input prompt in filter_tasks_flow()
- [x] T122 [US4] Add combined filter prompts in filter_tasks_flow() (ask for each filter type)
- [x] T123 [US4] Call manager.filter_tasks() with selected filters in filter_tasks_flow()
- [x] T124 [US4] Display result count "Showing X of Y tasks" in filter_tasks_flow()
- [x] T125 [US4] Display filtered results using existing task display format in filter_tasks_flow()
- [x] T126 [US4] Display "No tasks found matching filters" message for empty results in filter_tasks_flow()

### Menu Integration for User Story 4

- [x] T127 [US4] Update display_menu() to add option "9. Filter Tasks"
- [x] T128 [US4] Add route for choice "9" to call filter_tasks_flow() in main() event loop

**Checkpoint**: At this point, User Stories 2, 3, AND 4 should all work independently

---

## Phase 4: User Story 5 - Sort Tasks (Priority: P4)

**Goal**: Users can sort tasks by different criteria (created date, title, priority, status) in ascending or descending order

**Independent Test**: Create 5 tasks with different priorities, sort by priority, verify order is high → medium → low → none

### Implementation for User Story 5

- [x] T129 [US5] Implement sort_tasks(sort_by, reverse) method in phase1/src/task_manager.py
- [x] T130 [US5] Add priority mapping dictionary (high=3, medium=2, low=1, none=0) in sort_tasks()
- [x] T131 [US5] Add sort by "created" logic in sort_tasks() (uses created_at field)
- [x] T132 [US5] Add sort by "title" logic in sort_tasks() (case-insensitive, uses title.lower())
- [x] T133 [US5] Add sort by "priority" logic in sort_tasks() (uses priority_map)
- [x] T134 [US5] Add sort by "status" logic in sort_tasks() (uses completed field)
- [x] T135 [US5] Default priority sort to high→low (reverse=True for priority criteria)
- [x] T136 [US5] Return sorted copy of tasks (preserve original order in self.tasks)
- [x] T137 [US5] Add docstring to sort_tasks() method with type hints

### CLI Integration for User Story 5

- [x] T138 [US5] Implement sort_tasks_flow(manager) function in phase1/src/main.py
- [x] T139 [US5] Add sort criteria selection menu in sort_tasks_flow()
- [x] T140 [US5] Add options: "1. Created (newest)", "2. Created (oldest)", "3. Title (A-Z)", "4. Title (Z-A)"
- [x] T141 [US5] Add options: "5. Priority (high→low)", "6. Priority (low→high)", "7. Status"
- [x] T142 [US5] Map user choice to sort_by parameter and reverse flag in sort_tasks_flow()
- [x] T143 [US5] Call manager.sort_tasks() with selected criteria in sort_tasks_flow()
- [x] T144 [US5] Display sort criteria header "Sorted by: [criteria]" in sort_tasks_flow()
- [x] T145 [US5] Display sorted results using existing task display format in sort_tasks_flow()

### Menu Integration for User Story 5

- [x] T146 [US5] Update display_menu() to add option "10. Sort Tasks"
- [x] T147 [US5] Add route for choice "10" to call sort_tasks_flow() in main() event loop
- [x] T148 [US5] Update display_menu() to change "Exit" to option "11"
- [x] T149 [US5] Update get_user_choice() final validation to accept "11" for Exit
- [x] T150 [US5] Update main() event loop to check for choice "11" for Exit

**Checkpoint**: All 5 user stories (US1-US5) should now be independently functional

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final validation, and deployment readiness

- [x] T151 [P] Add docstrings to all new functions in phase1/src/main.py (set_priority_flow, manage_tags_flow, search_tasks_flow, filter_tasks_flow, sort_tasks_flow)
- [x] T152 [P] Add docstrings to all new methods in phase1/src/task_manager.py (set_priority, add_tags, remove_tags, search_tasks, filter_tasks, sort_tasks)
- [x] T153 [P] Update phase1/README.md with intermediate features section
- [x] T154 [P] Add priority management examples to phase1/README.md
- [x] T155 [P] Add tag management examples to phase1/README.md
- [x] T156 [P] Add search examples to phase1/README.md
- [x] T157 [P] Add filter examples to phase1/README.md
- [x] T158 [P] Add sort examples to phase1/README.md
- [x] T159 Validate all User Story 2 acceptance criteria (5 scenarios from spec.md)
- [x] T160 Validate all User Story 3 acceptance criteria (3 scenarios from spec.md)
- [x] T161 Validate all User Story 4 acceptance criteria (4 scenarios from spec.md)
- [x] T162 Validate all User Story 5 acceptance criteria (4 scenarios from spec.md)
- [x] T163 Validate edge case: 6 tags (should show error "Maximum 5 tags allowed")
- [x] T164 Validate edge case: Tag with special characters (should show error "Tags must be alphanumeric only")
- [x] T165 Validate edge case: Empty search keyword (should show all tasks)
- [x] T166 Validate edge case: Filter with no matches (should show "No tasks found matching filters")
- [x] T167 Validate edge case: Sort empty list (should show "No tasks yet!")
- [x] T168 Validate edge case: Invalid priority value "urgent" (should show error)
- [x] T169 Validate all new success criteria (SC-011 through SC-022 from spec.md)
- [x] T170 Test full intermediate demo workflow (<90 seconds per SC-021)
- [x] T171 Verify zero crashes during normal operation with intermediate features
- [x] T172 Test with 100+ tasks to ensure no performance degradation (SC-022)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Data Model Extension)**: Depends on Basic Level (001-console-todo-app) complete - BLOCKS all intermediate features
- **Phase 1 (US2 - Priorities & Tags)**: Depends on Phase 0 - Can start after data model extended
- **Phase 2 (US3 - Search)**: Depends on Phase 0 - Can run in parallel with Phase 1
- **Phase 3 (US4 - Filter)**: Depends on Phase 0 and Phase 1 (needs priority/tags) - Can run in parallel with Phase 2
- **Phase 4 (US5 - Sort)**: Depends on Phase 0 and Phase 1 (needs priority for sort) - Can run in parallel with Phases 2 and 3
- **Phase 5 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 2 (P1 - Priorities & Tags)**: Can start after Phase 0 - No dependencies on other intermediate stories
- **User Story 3 (P2 - Search)**: Can start after Phase 0 - Independent of US2 (but benefits from priority/tag display)
- **User Story 4 (P3 - Filter)**: Can start after Phase 0 - Uses priority/tags from US2 for filtering
- **User Story 5 (P4 - Sort)**: Can start after Phase 0 - Uses priority from US2 for sort criteria

### Within Each User Story

- US2: set_priority() → add_tags()/remove_tags() → CLI flows → display updates → menu integration
- US3: search_tasks() → CLI flow → menu integration
- US4: filter_tasks() → CLI flow → menu integration
- US5: sort_tasks() → CLI flow → menu integration

### Parallel Opportunities

- **Phase 0 (Data Model)**: T059-T062 can run sequentially (same file modifications)
- **Phase 1 (US2)**: T063-T073 (business logic) can precede T074-T095 (CLI integration)
- **Phase 5 (Polish)**: T151, T152, T153-T158 can all run in parallel (different files or sections)
- **Between User Stories**: Once Phase 0 complete, US2/US3/US4/US5 can be worked on in parallel by different developers (with US2 completing first for full integration)

---

## Parallel Example: After Phase 0

```bash
# After Data Model Extension (Phase 0), implement user stories in parallel:
Developer A: Implements User Story 2 (T063-T095) - Priorities & Tags
Developer B: Implements User Story 3 (T096-T109) - Search (needs US2 display updates for full integration)
Developer C: Implements User Story 4 (T110-T128) - Filter (needs US2 for filtering by priority/tags)
Developer D: Implements User Story 5 (T129-T150) - Sort (needs US2 for sort by priority)

# Note: US2 should complete first for best integration, but others can proceed independently
# Once all complete, all developers: Polish together (T151-T172)
```

---

## Implementation Strategy

### MVP First (User Story 2 Only)

1. Complete Phase 0: Data Model Extension (T059-T062)
2. Complete Phase 1: User Story 2 - Priorities & Tags (T063-T095)
3. **STOP and VALIDATE**: Manually test US2 acceptance scenarios
4. Demo priority and tag functionality

**Minimal Deliverable**: After completing through Phase 1, you have enhanced the basic app with organization features - users can categorize and prioritize their tasks.

### Incremental Delivery

1. Complete Phase 0 (T059-T062) → Data model extended
2. Add User Story 2 (T063-T095) → Test independently → **Deploy/Demo with priorities & tags!**
3. Add User Story 3 (T096-T109) → Test independently → Deploy/Demo (now with search)
4. Add User Story 4 (T110-T128) → Test independently → Deploy/Demo (now with filtering)
5. Add User Story 5 (T129-T150) → Test independently → Deploy/Demo (full intermediate features)
6. Complete Polish (T151-T172) → Final validation → **Production ready!**

Each story adds value without breaking previous stories.

### Sequential Strategy (Single Developer)

Recommended order:
1. Phase 0: Data Model Extension → 15 minutes
2. Phase 1: User Story 2 (Priorities & Tags) → 2.5 hours
3. Phase 2: User Story 3 (Search) → 45 minutes
4. Phase 3: User Story 4 (Filter) → 1.5 hours
5. Phase 4: User Story 5 (Sort) → 1.5 hours
6. Phase 5: Polish → 1.5 hours

**Total estimated time**: ~8 hours for complete intermediate implementation

### Parallel Team Strategy

With multiple developers:

1. Team completes Phase 0 together (T059-T062) → 15 minutes
2. Developer A: Complete User Story 2 (T063-T095) → 2.5 hours
3. Once US2 display updates are done, parallelize:
   - Developer B: User Story 3 (T096-T109) → 45 minutes
   - Developer C: User Story 4 (T110-T128) → 1.5 hours
   - Developer D: User Story 5 (T129-T150) → 1.5 hours
4. All developers: Polish together (T151-T172) → 1.5 hours

**Total elapsed time with 4 developers**: ~5.5 hours

---

## Task Details

### T059: Extend add_task() Method for Priority & Tags

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Modify add_task() method (currently at line 60-79)
- Add two new fields to task dictionary:
  - `"priority": "none"` (default priority level)
  - `"tags": []` (empty list for tags)
- Maintain existing fields (id, title, description, completed, created_at)

**Implementation Location**: task_manager.py:71-77

**Type Signature**: No change to method signature `def add_task(self, title: str, description: str = "") -> dict`

**Links**: [spec.md FR-016, FR-018], [plan.md Phase 0]

---

### T063: Implement set_priority() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int) and priority (str) parameters
- Validate priority is one of: "high", "medium", "low", "none"
- Call get_task(task_id) to find task
- If not found or invalid priority: return None
- If found and valid: update task["priority"] and return task

**Type Signature**: `def set_priority(self, task_id: int, priority: str) -> Optional[dict]`

**Links**: [spec.md FR-016, FR-017], [plan.md Decision 1]

---

### T067: Implement add_tags() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int) and new_tags (list[str]) parameters
- Call get_task(task_id) to find task
- If not found: return None
- For each tag in new_tags:
  - Validate: alphanumeric only (use tag.isalnum())
  - Validate: 1-20 characters length
  - Normalize: convert to lowercase
  - Skip if tag already in task["tags"] (duplicate prevention)
  - Check if total tags would exceed 5, return None if so
  - Append normalized tag to task["tags"]
- Return updated task

**Type Signature**: `def add_tags(self, task_id: int, new_tags: list[str]) -> Optional[dict]`

**Links**: [spec.md FR-018, FR-019, FR-020, FR-021], [plan.md Decision 2]

---

### T096: Implement search_tasks() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept keyword (str) parameter
- If keyword is empty/whitespace: return self.get_all_tasks()
- Convert keyword to lowercase for comparison
- Iterate through self.tasks
- For each task, check if keyword_lower in task["title"].lower() or task["description"].lower()
- Collect matching tasks in results list
- Return sorted results (newest first, by created_at)

**Type Signature**: `def search_tasks(self, keyword: str) -> list[dict]`

**Links**: [spec.md FR-022, FR-023], [plan.md Decision 3]

---

### T110: Implement filter_tasks() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept three Optional parameters: status (str), priority (str), tag (str)
- Start with results = self.tasks (all tasks)
- If status provided and not "all":
  - Filter results where status=="completed" matches task["completed"]==True
  - Filter results where status=="pending" matches task["completed"]==False
- If priority provided:
  - Filter results where task["priority"] == priority
- If tag provided:
  - Filter results where tag.lower() in task["tags"]
- Return sorted results (newest first, by created_at)

**Type Signature**: `def filter_tasks(self, status: Optional[str] = None, priority: Optional[str] = None, tag: Optional[str] = None) -> list[dict]`

**Links**: [spec.md FR-024, FR-025, FR-026], [plan.md Decision 4]

---

### T129: Implement sort_tasks() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept sort_by (str) and reverse (bool, default=False) parameters
- Define priority_map = {"high": 3, "medium": 2, "low": 1, "none": 0}
- Based on sort_by parameter:
  - "created": key = lambda t: t["created_at"]
  - "title": key = lambda t: t["title"].lower()
  - "priority": key = lambda t: priority_map[t["priority"]], flip reverse (high first by default)
  - "status": key = lambda t: t["completed"]
  - Invalid: raise ValueError
- Return sorted(self.tasks, key=key, reverse=reverse)

**Type Signature**: `def sort_tasks(self, sort_by: str, reverse: bool = False) -> list[dict]`

**Links**: [spec.md FR-027, FR-028], [plan.md Decision 5]

---

## Notes

- **[P] tasks** = different files/sections, no dependencies - can run in parallel
- **[Story] label** = maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- **No automated tests in Phase I** - manual validation only (per plan.md)
- Type hints required on all new methods (per constitution Code Quality standards)
- Zero external dependencies - Python stdlib only (per plan.md)
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

## Validation Checklist

After completing all tasks, verify:

- [ ] All 5 user stories work per acceptance scenarios (spec.md)
- [ ] All 15 new functional requirements met (FR-016 through FR-030)
- [ ] All 12 new success criteria met (SC-011 through SC-022)
- [ ] All edge cases handled (6 tags, special chars, empty search, no matches, invalid priority)
- [ ] Code follows Python PEP 8 style
- [ ] Type hints on all new methods
- [ ] Docstrings on all new functions
- [ ] README.md has clear documentation for all intermediate features
- [ ] Intermediate demo workflow completes in <90 seconds
- [ ] Zero crashes during normal operation with intermediate features
- [ ] Works with 100+ tasks without performance degradation

## Next Steps

After completing tasks.md:
1. Run `/sp.implement` to execute all tasks sequentially
2. Perform manual validation against checklist above
3. Create demo video (<90 seconds showing all intermediate features)
4. Update README.md with comprehensive examples
5. Commit to git with message: "feat: add priorities, tags, search, filter, sort to Phase I console app"
6. Proceed to Phase II planning (web application with persistence)
