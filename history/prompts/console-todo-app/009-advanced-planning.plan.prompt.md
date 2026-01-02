---
id: 009
title: Advanced Level Planning
stage: plan
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: console-todo-app
branch: 003-todo-advanced
user: Waqas35201
command: /sp.plan
labels: ["planning", "advanced", "recurring-tasks", "due-dates", "reminders", "threading", "phase1"]
links:
  spec: phase1/specs/003-todo-advanced/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - phase1/specs/003-todo-advanced/plan.md
 - phase1/specs/003-todo-advanced/checklists/plan-quality-checklist.md
tests:
 - Constitution compliance check: PASSED (all 4 principles verified)
 - Plan quality validation: PASSED (all checkboxes complete)
 - Thread safety analysis: PASSED (Lock + Queue strategy documented)
---

## Prompt

```
/sp.plan

[User provided detailed architectural plan with 3-component architecture (main.py, task_manager.py, reminder_thread.py), recurrence logic with cloning strategy, thread-safe background reminder checking, date calculation algorithms, and comprehensive implementation flow]
```

## Response snapshot

Successfully created implementation plan for Console Todo App - Advanced Level.

**Plan Summary**:

**Technical Context**:
- Extends existing Intermediate Level (task_manager.py + main.py)
- Adds NEW module: `reminder_thread.py` for background reminder checking
- Adds 4 new fields to task schema: recurrence, due_date, reminder, parent_task_id
- Zero external dependencies (stdlib only: threading, datetime, calendar, queue)
- Thread-safe design with Lock + Queue hybrid

**3-Component Architecture**:

1. **main.py (CLI Interface)**:
   - Add 5 new flow functions for menu options 11-15
   - Update display to show recurrence indicators, due dates, overdue emphasis
   - Check notification queue before menu display
   - Handle snooze/dismiss actions for reminders

2. **task_manager.py (Business Logic)**:
   - Add 10 new methods: set_recurrence, create_next_occurrence, calculate_next_due_date, set_due_date, set_reminder, get_overdue_tasks, get_upcoming_tasks, get_pending_reminders, mark_reminder_notified, snooze_reminder
   - Add threading.Lock for thread-safe task list access
   - Implement recurrence cloning strategy (new task on completion)
   - Real-time overdue calculation (no cached flags)

3. **reminder_thread.py (Background Worker)** ⚙️ NEW:
   - ReminderThread class extends threading.Thread
   - Daemon thread (auto-stops with main app)
   - Checks reminders every 60 seconds
   - Uses Queue for thread-safe notifications
   - Marks reminders as notified to prevent duplicates

**5 Design Decisions Documented**:

1. **Recurring Task Implementation**: Clone task on completion (chosen)
   - Trade-off: Clone creates audit trail vs single task simpler
   - Rationale: Preserves history, each occurrence independent, parent_task_id links original

2. **Reminder Check Frequency**: 60-second interval (chosen)
   - Trade-off: 60s balanced vs 10s responsive vs event-driven efficient
   - Rationale: Acceptable precision (0-59s late), low CPU usage, simple implementation

3. **Thread Safety Strategy**: Lock + Queue hybrid (chosen)
   - Trade-off: Lock+Queue vs Queue-only vs no threading
   - Rationale: Lock protects shared data, Queue thread-safe by design, standard producer-consumer pattern

4. **Due Date Storage Format**: ISO string format (chosen)
   - Trade-off: ISO string vs datetime object vs Unix timestamp
   - Rationale: JSON-serializable for Phase II, human-readable, Python built-in support

5. **Overdue Calculation**: Real-time on display (chosen)
   - Trade-off: Real-time always accurate vs cached flag faster vs separate list
   - Rationale: Always accurate, no stale data, acceptable O(n) for Phase I

**6 Implementation Phases**:
- **Phase 0**: Data Model Extension (add 4 new fields + threading.Lock)
- **Phase 1**: Recurring Task Logic (US1 - clone strategy, date calculations, display indicators)
- **Phase 2**: Due Date Management (US2 - validation, countdowns, overdue filtering, sorting)
- **Phase 3**: Reminder System Data Layer (US3 - store offset + notified flag, validation)
- **Phase 4**: Background Reminder Thread (US3 - ReminderThread class, Queue notifications, mark notified)
- **Phase 5**: Menu Integration & Display Updates (add options 11-15, update task display)
- **Phase 6**: Polish & Documentation (README updates, validation, demo)

**Files to Modify/Create**:
- **Modify**: `phase1/src/task_manager.py` (add 10 methods + Lock)
- **Modify**: `phase1/src/main.py` (add 5 flows + notification handling + display updates)
- **Create**: `phase1/src/reminder_thread.py` (NEW file - ReminderThread class) ⚙️
- **Update**: `phase1/README.md` (document all 10 features)

**Thread Safety Implementation**:
- `threading.Lock()` in TaskManager.__init__ for shared task list
- `with self.lock:` pattern for all task list access
- `Queue()` for thread-safe notifications (no locking needed)
- Daemon thread (`daemon=True`) for clean shutdown
- Graceful stop with `self.running` flag

**Recurrence Cloning Logic**:
```python
# When recurring task marked complete:
1. Check if task.recurrence exists
2. Calculate next_due_date based on type (daily/weekly/monthly)
3. Clone task with new ID
4. Reset completed = False
5. Link via parent_task_id = original_task_id
6. Append new task to list
7. Return both completed task and new occurrence
```

**Date Calculation Edge Cases**:
- Monthly on day 31 → use `min(current_day, last_day_of_month)` (e.g., Jan 31 → Feb 28/29)
- Early completion → next based on original schedule (not completion date)
- Timezone: Use local system timezone only (no conversion)

**Reminder Flow**:
```
[Every 60 seconds]
ReminderThread → check current_time >= (due_date - offset_minutes)
→ if yes: Queue.put(task) + mark_reminder_notified(task_id)

[Main thread before menu]
Check Queue.empty() → if notification: display + prompt (snooze/view/continue)
```

**Constitution Compliance**: ✅ All 4 principles verified
- Spec-First Development: Plan follows approved spec 003
- AI-Native Architecture: Claude Code generates 100% of code
- Code Quality Standards: Type hints + docstrings + thread safety required
- Progressive Enhancement: Backward compatible with Intermediate Level

**Plan Quality**: ✅ PASSED (all checkboxes complete + thread safety analysis)

**Risks Identified & Mitigated**:
1. Thread safety issues → Use Lock + Queue + daemon thread
2. Month-end date calculations → Use calendar.monthrange() for last day
3. Background thread not stopping → Use daemon=True (auto-stops with app)
4. Notification blocking CLI → Check queue non-blocking before menu

## Outcome

- ✅ Impact: Advanced Level plan complete - ready for task breakdown with background threading
- 🧪 Tests: Constitution check PASSED, Plan quality checklist PASSED, Thread safety analysis PASSED
- 📁 Files: 2 files created (plan.md + quality checklist)
- 🔁 Next prompts: `/sp.tasks` to generate task breakdown (~80 tasks), then `/sp.implement`
- 🧠 Reflection: 3-component architecture is well-defined. Thread safety strategy (Lock + Queue) follows standard patterns. Recurrence cloning strategy preserves history while keeping implementation simple. All 5 design decisions have clear rationale with code examples. Edge cases thoroughly documented (month-end, early completion, thread lifecycle). Ready for task generation.

## Evaluation notes (flywheel)

- Failure modes observed: None - planning straightforward, user provided comprehensive architecture
- Graders run and results (PASS/FAIL): Constitution check - PASS, Plan quality validation - PASS, Thread safety analysis - PASS
- Prompt variant (if applicable): N/A (first planning iteration for advanced level)
- Next experiment (smallest change to try): Generate task breakdown with `/sp.tasks`, ensuring tasks cover all 6 phases with clear thread safety requirements and date calculation edge cases
