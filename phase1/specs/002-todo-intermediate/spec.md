# Feature Specification: Console Todo App - Intermediate Level

**Feature Branch**: `002-todo-intermediate`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "Phase I: Todo Console App (Intermediate Level) - Add priorities, tags, search, filter, and sort features to existing basic console app"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic CRUD Operations (Priority: P0 - Already Implemented)

As a user, I have a functional todo app with create, view, update, delete, and mark complete features.

**Why this priority**: Foundation already exists from basic implementation

**Independent Test**: Already tested and working

**Acceptance Scenarios**: See spec 001-console-todo-app

---

### User Story 2 - Priorities & Tags (Priority: P1)

As a user, I can assign priority levels and tags to my tasks so that I can organize and categorize them effectively.

**Why this priority**: Organization is fundamental - users need to categorize tasks before searching/filtering

**Independent Test**: Create task with priority "high" and tags "work,urgent", verify they display correctly with [H] indicator and #work #urgent tags

**Acceptance Scenarios**:

1. **Given** I'm creating a new task, **When** I set priority to "high" and tags to "work,urgent", **Then** the task displays as "[H] Task Title #work #urgent"
2. **Given** an existing task, **When** I update its priority from "none" to "medium", **Then** the task displays with [M] indicator
3. **Given** an existing task with tags "work,home", **When** I add tag "urgent", **Then** the task shows "#work #home #urgent"
4. **Given** I enter more than 5 tags, **When** I try to save, **Then** I see error "Maximum 5 tags allowed"
5. **Given** I enter a tag with 25 characters, **When** I try to save, **Then** I see error "Tag max 20 characters"

---

### User Story 3 - Search Tasks (Priority: P2)

As a user, I can search for tasks by keyword so that I can quickly find specific tasks.

**Why this priority**: After organization, finding tasks is the next most important feature

**Independent Test**: Create tasks with different titles/descriptions, search for "groceries", verify only matching tasks appear

**Acceptance Scenarios**:

1. **Given** 10 tasks exist with various titles, **When** I search for "presentation", **Then** I see only tasks containing "presentation" in title or description (case-insensitive)
2. **Given** I search for "xyz123", **When** no tasks match, **Then** I see message "No tasks found matching 'xyz123'"
3. **Given** I search for "work", **When** 3 tasks match, **Then** results show "Found 3 tasks:" followed by the matching tasks

---

### User Story 4 - Filter Tasks (Priority: P3)

As a user, I can filter tasks by status, priority, or tags so that I can focus on specific subsets of tasks.

**Why this priority**: Filtering complements search for task management

**Independent Test**: Create tasks with different priorities and statuses, filter by "high priority + pending status", verify only matching tasks appear

**Acceptance Scenarios**:

1. **Given** 10 tasks with mixed statuses, **When** I filter by "pending" status, **Then** I see only incomplete tasks with count "Showing X of 10 tasks"
2. **Given** tasks with different priorities, **When** I filter by "high" priority, **Then** I see only high-priority tasks
3. **Given** tasks with various tags, **When** I filter by tag "work", **Then** I see only tasks tagged with "work"
4. **Given** I apply multiple filters (status=pending, priority=high), **When** results are shown, **Then** only tasks matching ALL filters appear

---

### User Story 5 - Sort Tasks (Priority: P4)

As a user, I can sort tasks by different criteria so that I can view tasks in my preferred order.

**Why this priority**: Sorting enhances viewing but is less critical than search/filter

**Independent Test**: Create 5 tasks with different priorities, sort by priority, verify order is high → medium → low → none

**Acceptance Scenarios**:

1. **Given** tasks with mixed creation dates, **When** I sort by "created (newest)", **Then** most recent tasks appear first
2. **Given** tasks with different priorities, **When** I sort by "priority", **Then** order is: high priority → medium → low → none
3. **Given** tasks with titles "Zebra", "Apple", "Mango", **When** I sort by "title (A-Z)", **Then** order is: Apple, Mango, Zebra
4. **Given** current sort is "priority (high → low)", **When** displayed, **Then** header shows "Sorted by: Priority (high → low)"

---

### Edge Cases

- What happens when a user enters 6 tags? → System shows error "Maximum 5 tags allowed"
- What happens when a tag has special characters? → System shows error "Tags must be alphanumeric only"
- What happens when searching with empty keyword? → System shows all tasks
- What happens when filtering with no matches? → System shows "No tasks found matching filters"
- What happens when sorting empty list? → System shows "No tasks yet!"
- What happens when updating priority to invalid value "urgent"? → System shows error "Invalid priority. Use: high, medium, low, none"

## Requirements *(mandatory)*

### Functional Requirements

**Existing Requirements (from Basic Level)**:
- FR-001 through FR-015: All existing basic requirements remain

**New Requirements (Intermediate Level)**:

- **FR-016**: System MUST support priority levels: high, medium, low, none (default)
- **FR-017**: System MUST display priority indicators: [H] for high, [M] for medium, [L] for low, no indicator for none
- **FR-018**: System MUST allow 0-5 tags per task
- **FR-019**: System MUST validate tags: alphanumeric only, 1-20 characters each
- **FR-020**: System MUST store tags as lowercase strings
- **FR-021**: System MUST display tags with # prefix (e.g., #work #urgent)
- **FR-022**: System MUST provide search functionality for title and description (case-insensitive)
- **FR-023**: System MUST show search result count and "No tasks found" message for empty results
- **FR-024**: System MUST provide filter options: status (all/pending/completed), priority (high/medium/low/none), tag (specific tag name)
- **FR-025**: System MUST support combined filters (AND logic: status + priority, status + tag, etc.)
- **FR-026**: System MUST display filter result count: "Showing X of Y tasks"
- **FR-027**: System MUST provide sort options: created (newest/oldest), title (A-Z/Z-A), priority (high→low/low→high), status
- **FR-028**: System MUST display current sort criteria in view header
- **FR-029**: System MUST update menu to include options 6-10 for new features
- **FR-030**: Priority and tags MUST be optional during task creation (defaults: priority=none, tags=[])

### Key Entities

- **Task** (updated from basic level):
  - `id` (integer): Unique auto-incrementing identifier
  - `title` (string, required): Task name (1-200 chars)
  - `description` (string, optional): Extended details (max 1000 chars)
  - `completed` (boolean): Status indicator (default False)
  - `priority` (string): Priority level - "high", "medium", "low", "none" (default "none")
  - `tags` (list of strings): Category tags (0-5 tags, each 1-20 chars, alphanumeric, lowercase)
  - `created_at` (datetime): Timestamp of creation

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Existing Criteria (from Basic Level)**:
- SC-001 through SC-010: All existing success criteria remain

**New Criteria (Intermediate Level)**:

- **SC-011**: Users can assign priority to a task in <5 seconds
- **SC-012**: Users can add/remove tags to a task in <10 seconds
- **SC-013**: Users can search for tasks and see results in <3 seconds
- **SC-014**: Users can apply filters and see filtered results in <3 seconds
- **SC-015**: Users can sort tasks by any criterion in <2 seconds
- **SC-016**: Priority indicators ([H], [M], [L]) display correctly in all views
- **SC-017**: Tag display (#tag format) appears correctly in all views
- **SC-018**: Search finds matches in both title and description (case-insensitive)
- **SC-019**: Combined filters work correctly (e.g., "high priority + pending status")
- **SC-020**: Sort order displays correctly for all sort options
- **SC-021**: Full intermediate demo workflow completes in <90 seconds
- **SC-022**: All new features work with 100+ tasks without performance degradation

## Assumptions

1. **Existing Implementation**: Basic Level (001-console-todo-app) is fully implemented and working
2. **Code Reuse**: Will extend existing TaskManager and main.py rather than rewriting
3. **Backward Compatibility**: Existing tasks without priority/tags will default to priority="none", tags=[]
4. **User Environment**: Users have Python 3.13+ and can run command-line applications
5. **Data Migration**: Existing in-memory tasks will be enhanced with new fields
6. **Tag Format**: Tags are single words (no spaces), comma-separated input, displayed with # prefix
7. **Priority Validation**: Only exact matches for "high", "medium", "low", "none" accepted (case-insensitive)
8. **Filter Logic**: Multiple filters use AND logic (must match ALL criteria)
9. **Sort Stability**: When sorting, tasks with equal sort keys maintain their relative order
10. **Search Behavior**: Empty search keyword returns all tasks (equivalent to View All)

## Out of Scope

The following are explicitly NOT included in Intermediate Level:

- Persistent storage (file/database) - deferred to Phase II
- User authentication/multiple users - deferred to Phase II
- Due dates and reminders - deferred to Advanced level
- Recurring tasks - deferred to Advanced level
- Task dependencies - deferred to Advanced level
- Subtasks or nested tasks - deferred to Advanced level
- Export/import functionality - deferred to Advanced level
- Undo/redo operations - deferred to Advanced level
- Task templates - deferred to Advanced level
- Web interface or GUI - deferred to Phase II
- Natural language input - deferred to Advanced level
- Task history/audit trail - deferred to Advanced level

## Implementation Notes

This intermediate spec builds on the existing basic implementation (001-console-todo-app). The implementation approach should:

1. **Extend Existing Code**: Modify task_manager.py to add priority and tags fields
2. **Update Data Structure**: Add priority and tags to task dictionary
3. **Add New Methods**: Implement search_tasks(), filter_tasks(), sort_tasks() in TaskManager
4. **Extend CLI**: Add new menu options (6-10) and corresponding flow functions in main.py
5. **Update Display**: Modify view_tasks_flow() to show priority indicators and tags
6. **Maintain Compatibility**: Ensure existing basic features (US1-US5) continue to work

## Dependencies

- **Requires**: Spec 001-console-todo-app (Basic Level) must be implemented and working
- **Blocks**: None - this is an iterative enhancement
- **Related**: Phase II will add persistence to both basic and intermediate features
