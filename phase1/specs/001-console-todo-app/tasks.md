---
description: "Task list for Console Todo App implementation"
---

# Tasks: Console Todo App

**Input**: Design documents from `phase1/specs/001-console-todo-app/`
**Prerequisites**: plan.md (completed), spec.md (completed)

**Tests**: No automated tests in Phase I - manual validation only. Testing infrastructure deferred to Phase II per plan.md.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Project root**: `phase1/`
- **Source code**: `phase1/src/`
- **Documentation**: `phase1/` (README.md)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create phase1/src/ directory structure
- [x] T002 Initialize Python 3.13+ project with UV in phase1/ directory
- [x] T003 [P] Create phase1/pyproject.toml with project metadata
- [x] T004 [P] Create phase1/.python-version file specifying Python 3.13
- [x] T005 [P] Create phase1/src/__init__.py as package marker
- [x] T006 [P] Create empty phase1/src/main.py file
- [x] T007 [P] Create empty phase1/src/task_manager.py file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: TaskManager data layer - MUST be complete before ANY user story implementation

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T008 Implement TaskManager class with __init__() in phase1/src/task_manager.py
- [x] T009 Implement _generate_id() private method in phase1/src/task_manager.py
- [x] T010 Add type imports (datetime, Optional) to phase1/src/task_manager.py
- [x] T011 Implement get_task(task_id) method in phase1/src/task_manager.py
- [x] T012 Implement get_all_tasks() method with sorting in phase1/src/task_manager.py

**Checkpoint**: TaskManager foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Create and View Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create tasks with title/description and view their task list

**Independent Test**: Launch app, create 2-3 tasks, verify they appear in list with correct ID, title, status, and description preview (50 chars)

### Implementation for User Story 1

- [x] T013 [US1] Implement add_task(title, description) method in phase1/src/task_manager.py
- [x] T014 [US1] Implement display_menu() function in phase1/src/main.py
- [x] T015 [US1] Implement get_user_choice() function with validation in phase1/src/main.py
- [x] T016 [US1] Implement add_task_flow(manager) function in phase1/src/main.py
- [x] T017 [US1] Implement view_tasks_flow(manager) function in phase1/src/main.py
- [x] T018 [US1] Implement main() function with event loop in phase1/src/main.py
- [x] T019 [US1] Add input validation for title (1-200 chars) in phase1/src/main.py
- [x] T020 [US1] Add input validation for description (max 1000 chars) in phase1/src/main.py
- [x] T021 [US1] Add empty list message "No tasks yet!" in view_tasks_flow()
- [x] T022 [US1] Add task confirmation message showing ID in add_task_flow()

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create and view tasks

---

## Phase 4: User Story 2 - Mark Tasks Complete (Priority: P2)

**Goal**: Users can toggle task completion status with visual indicator

**Independent Test**: Create a task, mark it complete (verify ✓ shown), mark incomplete (verify [ ] shown), try non-existent ID (verify error)

### Implementation for User Story 2

- [x] T023 [US2] Implement toggle_complete(task_id) method in phase1/src/task_manager.py
- [x] T024 [US2] Implement toggle_complete_flow(manager) function in phase1/src/main.py
- [x] T025 [US2] Add visual indicators [✓] for completed and [ ] for pending in view_tasks_flow()
- [x] T026 [US2] Add menu option "5. Mark Complete/Incomplete" in display_menu()
- [x] T027 [US2] Add route for choice "5" in main() event loop
- [x] T028 [US2] Add error message "Task ID X not found" for invalid IDs

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Update Task Details (Priority: P3)

**Goal**: Users can modify task title or description with before/after confirmation

**Independent Test**: Create a task, update its title, verify before/after message shown and change persists in list view

### Implementation for User Story 3

- [x] T029 [US3] Implement update_task(task_id, title, description) method in phase1/src/task_manager.py
- [x] T030 [US3] Implement update_task_flow(manager) function in phase1/src/main.py
- [x] T031 [US3] Add input prompts for task ID and new title/description
- [x] T032 [US3] Add before/after confirmation display in update_task_flow()
- [x] T033 [US3] Add menu option "3. Update Task" in display_menu()
- [x] T034 [US3] Add route for choice "3" in main() event loop
- [x] T035 [US3] Add validation for updated title (1-200 chars) and description (max 1000 chars)
- [x] T036 [US3] Add error message "Task ID X not found" for invalid IDs

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P4)

**Goal**: Users can remove tasks with explicit confirmation (y/n)

**Independent Test**: Create a task, delete it with "y" confirmation (verify removed), create another, try delete with "n" (verify remains)

### Implementation for User Story 4

- [x] T037 [US4] Implement delete_task(task_id) method in phase1/src/task_manager.py
- [x] T038 [US4] Implement delete_task_flow(manager) function in phase1/src/main.py
- [x] T039 [US4] Add confirmation prompt "Delete task ID X? (y/n)" in delete_task_flow()
- [x] T040 [US4] Add confirmation validation (accept y/n, case-insensitive)
- [x] T041 [US4] Add menu option "4. Delete Task" in display_menu()
- [x] T042 [US4] Add route for choice "4" in main() event loop
- [x] T043 [US4] Add success message "Task deleted" on confirmation
- [x] T044 [US4] Add error message "Task ID X not found" for invalid IDs

**Checkpoint**: All 4 user stories should now be independently functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final validation, and deployment readiness

- [x] T045 [P] Add docstrings to all functions in phase1/src/main.py
- [x] T046 [P] Add docstrings to all methods in phase1/src/task_manager.py
- [x] T047 [P] Create phase1/README.md with setup instructions
- [x] T048 [P] Add usage examples to phase1/README.md
- [x] T049 [P] Add features and limitations sections to phase1/README.md
- [x] T050 Validate all User Story 1 acceptance criteria (spec.md)
- [ ] T051 Validate all User Story 2 acceptance criteria (spec.md)
- [ ] T052 Validate all User Story 3 acceptance criteria (spec.md)
- [ ] T053 Validate all User Story 4 acceptance criteria (spec.md)
- [ ] T054 Validate all edge cases (title/description limits, invalid inputs)
- [ ] T055 Validate all 10 success criteria (SC-001 through SC-010 from spec.md)
- [ ] T056 Test full demo workflow (<90 seconds per SC-008)
- [ ] T057 Verify zero crashes during normal operation (SC-009)
- [ ] T058 Test on WSL 2, Linux, and macOS (SC-010)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) - BLOCKS all user stories
- **User Stories (Phases 3-6)**: All depend on Foundational (Phase 2) completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → P4)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 (view_tasks_flow) but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Integrates with US1 (menu loop) but independently testable
- **User Story 4 (P4)**: Can start after Foundational (Phase 2) - Integrates with US1 (menu loop) but independently testable

### Within Each User Story

- US1: add_task() method → CLI flows → input validation → messages
- US2: toggle_complete() method → CLI flow → visual indicators → menu integration
- US3: update_task() method → CLI flow → validation → before/after display → menu integration
- US4: delete_task() method → CLI flow → confirmation → menu integration

### Parallel Opportunities

- **Phase 1 (Setup)**: T003, T004, T005, T006, T007 can all run in parallel after T001-T002
- **Phase 2 (Foundational)**: T010, T011, T012 can run in parallel after T008-T009
- **Phase 7 (Polish)**: T045, T046, T047, T048, T049 can all run in parallel
- **Between User Stories**: Once Phase 2 complete, US1, US2, US3, US4 can be worked on in parallel by different developers

---

## Parallel Example: User Story 1

```bash
# After Foundational phase, implement US1 sequentially:
# 1. Data layer first (T013)
# 2. Then CLI functions in parallel:
Task T014: "Implement display_menu() function in phase1/src/main.py"
Task T015: "Implement get_user_choice() function with validation in phase1/src/main.py"
Task T016: "Implement add_task_flow(manager) function in phase1/src/main.py"
Task T017: "Implement view_tasks_flow(manager) function in phase1/src/main.py"
# 3. Then main loop and validation (T018-T022 sequentially)
```

---

## Parallel Example: All User Stories

```bash
# After Foundational phase (T008-T012), user stories can proceed in parallel:
Developer A: Implements User Story 1 (T013-T022)
Developer B: Implements User Story 2 (T023-T028) - waits for US1 menu structure
Developer C: Implements User Story 3 (T029-T036) - waits for US1 menu structure
Developer D: Implements User Story 4 (T037-T044) - waits for US1 menu structure

# Note: US2, US3, US4 depend on US1 menu framework (T014, T015, T018)
# So in practice: Complete US1 first, then US2/US3/US4 can proceed in parallel
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T007)
2. Complete Phase 2: Foundational (T008-T012) - CRITICAL
3. Complete Phase 3: User Story 1 (T013-T022)
4. **STOP and VALIDATE**: Manually test US1 acceptance scenarios
5. Demo basic create/view functionality

**Minimal Deliverable**: After completing through Phase 3, you have a working MVP that demonstrates the core value proposition - users can track their to-do items.

### Incremental Delivery

1. Complete Setup + Foundational (T001-T012) → Foundation ready
2. Add User Story 1 (T013-T022) → Test independently → **Deploy/Demo MVP!**
3. Add User Story 2 (T023-T028) → Test independently → Deploy/Demo (now with completion tracking)
4. Add User Story 3 (T029-T036) → Test independently → Deploy/Demo (now with editing)
5. Add User Story 4 (T037-T044) → Test independently → Deploy/Demo (full CRUD complete)
6. Complete Polish (T045-T058) → Final validation → **Production ready!**

Each story adds value without breaking previous stories.

### Sequential Strategy (Single Developer)

Recommended order:
1. Phase 1: Setup → 15 minutes
2. Phase 2: Foundational → 30 minutes
3. Phase 3: User Story 1 → 1.5 hours
4. Phase 4: User Story 2 → 45 minutes
5. Phase 5: User Story 3 → 1 hour
6. Phase 6: User Story 4 → 45 minutes
7. Phase 7: Polish → 1 hour

**Total estimated time**: ~6 hours for complete implementation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T012) → 45 minutes
2. Developer A: Complete User Story 1 (T013-T022) → 1.5 hours
3. Once US1 menu framework is done, parallelize:
   - Developer B: User Story 2 (T023-T028) → 45 minutes
   - Developer C: User Story 3 (T029-T036) → 1 hour
   - Developer D: User Story 4 (T037-T044) → 45 minutes
4. All developers: Polish together (T045-T058) → 1 hour

**Total elapsed time with 4 developers**: ~3.5 hours

---

## Task Details

### T013: Implement add_task() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept title (str) and description (str, optional)
- Generate unique ID using _generate_id()
- Create task dictionary with all fields (id, title, description, completed=False, created_at)
- Append task to self.tasks list
- Return created task dictionary

**Type Signature**: `def add_task(self, title: str, description: str = "") -> dict`

**Links**: [spec.md User Story 1], [plan.md Component 2]

---

### T016: Implement add_task_flow() Function

**File**: `phase1/src/main.py`

**Functionality**:
- Prompt user for task title (input())
- Prompt user for task description (input(), optional - allow empty)
- Validate title length (1-200 chars) - show error if invalid
- Validate description length (max 1000 chars) - show error if invalid
- Call manager.add_task(title, description)
- Display confirmation: "Task #X created: [title]"

**Type Signature**: `def add_task_flow(manager: TaskManager) -> None`

**Links**: [spec.md FR-002, FR-003, FR-009]

---

### T017: Implement view_tasks_flow() Function

**File**: `phase1/src/main.py`

**Functionality**:
- Call manager.get_all_tasks()
- If empty: print "No tasks yet! Create your first task to get started."
- If not empty: loop through tasks and display:
  - Visual indicator: [✓] if completed, [ ] if pending (added in US2)
  - Format: `ID. Title (Status) - Description preview (50 chars)`
  - Example: `[ ] 1. Buy groceries (Pending) - Milk, eggs, bread...`

**Type Signature**: `def view_tasks_flow(manager: TaskManager) -> None`

**Links**: [spec.md FR-006, FR-007]

---

### T023: Implement toggle_complete() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int)
- Call get_task(task_id) to find task
- If not found: return None
- If found: flip task["completed"] boolean (True ↔ False)
- Return updated task dictionary

**Type Signature**: `def toggle_complete(self, task_id: int) -> Optional[dict]`

**Links**: [spec.md User Story 2], [plan.md Decision 4]

---

### T029: Implement update_task() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int), title (Optional[str]), description (Optional[str])
- Call get_task(task_id) to find task
- If not found: return None
- If title provided: update task["title"]
- If description provided: update task["description"]
- Return updated task dictionary

**Type Signature**: `def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> Optional[dict]`

**Links**: [spec.md User Story 3], [plan.md Component 2]

---

### T037: Implement delete_task() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int)
- Loop through self.tasks to find task with matching ID
- If found: remove from list (self.tasks.remove(task)), return True
- If not found: return False

**Type Signature**: `def delete_task(self, task_id: int) -> bool`

**Links**: [spec.md User Story 4], [plan.md Component 2]

---

## Notes

- **[P] tasks** = different files, no dependencies - can run in parallel
- **[Story] label** = maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- **No automated tests in Phase I** - manual validation only (per plan.md Technical Context)
- Type hints required on all functions (per constitution Code Quality standards)
- Zero external dependencies - Python stdlib only (per plan.md)
- **Avoid**: vague tasks, same file conflicts, cross-story dependencies that break independence

## Validation Checklist

After completing all tasks, verify:

- [ ] All 4 user stories work per acceptance scenarios (spec.md)
- [ ] All 15 functional requirements met (FR-001 through FR-015)
- [ ] All 10 success criteria met (SC-001 through SC-010)
- [ ] All edge cases handled (empty inputs, max lengths, invalid IDs)
- [ ] Code follows Python PEP 8 style
- [ ] Type hints on all functions
- [ ] Docstrings on all functions
- [ ] README.md has clear setup/run instructions
- [ ] Demo workflow completes in <90 seconds
- [ ] Zero crashes during normal operation
- [ ] Works on WSL 2, Linux, and macOS

## Next Steps

After completing tasks.md:
1. Run `/sp.implement` to execute all tasks
2. Perform manual validation against checklist above
3. Create demo video (<90 seconds showing all 4 user stories)
4. Commit to git with message: "feat: implement Phase I console todo app"
5. Proceed to Phase II planning (web application with persistence)
