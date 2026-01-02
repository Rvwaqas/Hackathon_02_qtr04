---
id: 010
title: Advanced Level Task Breakdown
stage: tasks
date: 2025-12-31
surface: agent
model: claude-sonnet-4-5-20250929
feature: console-todo-app
branch: 003-todo-advanced
user: Waqas35201
command: /sp.tasks
labels: ["tasks", "advanced", "recurring-tasks", "due-dates", "reminders", "threading", "phase1"]
links:
  spec: phase1/specs/003-todo-advanced/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - phase1/specs/003-todo-advanced/tasks.md
tests:
 - Task format validation: PASSED (all tasks follow checklist format with ID, [US#] labels, file paths)
 - User story mapping: PASSED (all 3 advanced stories mapped to phases)
 - Dependency analysis: PASSED (clear phase dependencies, thread safety requirements documented)
 - Thread safety requirements: PASSED (Lock usage and Queue usage specified in tasks)
---

## Prompt

```
/sp.tasks

[User provided task examples with detailed implementation for:
- Data model extension (recurrence, due_date, reminder, parent_task_id fields)
- Recurrence management (set_recurrence, calculate_next_due_date, create_next_occurrence)
- Due date management (set_due_date, get_overdue_tasks, get_upcoming_tasks)
- Reminder management (set_reminder, get_pending_reminders, mark_reminder_notified, snooze_reminder)
- Background thread (ReminderThread class with check_reminders every 60s)
- CLI flows (set_recurrence_flow, set_due_date_flow, set_reminder_flow, view_overdue_flow, view_upcoming_flow)
- Display updates (format with due dates, recurrence, overdue emphasis)
- Menu updates (add options 11-15, Exit becomes 16)]
```

## Response snapshot

Successfully generated comprehensive task breakdown for Console Todo App - Advanced Level.

**Tasks Summary**:

**Total Tasks**: 248 tasks (T173-T420) organized across 7 phases

**Phase Breakdown**:
- **Phase 0**: Data Model Extension (8 tasks: T173-T180) - Foundation with threading.Lock
- **Phase 1**: User Story 1 - Recurring Tasks (47 tasks: T181-T227) - P1 High Impact
- **Phase 2**: User Story 2 - Due Dates (50 tasks: T228-T277) - P2
- **Phase 3**: User Story 3 - Reminders Data Layer (32 tasks: T278-T309) - P3
- **Phase 4**: User Story 3 - Background Thread (46 tasks: T310-T355) - P3 Continuation
- **Phase 5**: Menu & Display Integration (13 tasks: T356-T368) - Cross-cutting
- **Phase 6**: Polish & Validation (52 tasks: T369-T420) - Documentation + Testing

**User Story Mapping**:
- **US1 (P1)**: 47 tasks covering recurring task logic, cloning strategy, next occurrence calculation, CLI flows, display indicators
- **US2 (P2)**: 50 tasks covering due date management, overdue detection, upcoming filter, countdown display, sort integration
- **US3 (P3)**: 78 tasks (32 data + 46 thread) covering reminder storage, background thread, notification display, snooze functionality

**Task Format**: All 248 tasks follow strict checklist format:
- ✅ Checkbox prefix `- [ ]`
- ✅ Sequential Task IDs (T173-T420)
- ✅ [P] markers for parallelizable tasks (10 tasks in Phase 6)
- ✅ [US1], [US2], [US3] story labels
- ✅ Clear descriptions with exact file paths
- ✅ Thread safety requirements specified where needed

**Dependency Structure**:
- **Phase 0 blocks all**: Data model + threading.Lock must complete first
- **Phase 1 & 2 can parallelize**: Recurring tasks and due dates are independent
- **Phase 3 depends on Phase 2**: Reminders require due dates to exist
- **Phase 4 sequential after Phase 3**: Background thread needs reminder methods
- **Phase 5 after 1, 2, 3**: Menu integration unifies all features
- **Phase 6 depends on desired stories**: Polish after implementing selected features

**Independent Testing**:
- US1: Create daily recurring → mark complete → verify next created for tomorrow
- US2: Set due date in future → verify countdown "in 2 days", let become overdue → verify "OVERDUE by X hours"
- US3: Set reminder 1 hour before → wait → verify "⏰ REMINDER" notification with snooze option

**Thread Safety Specifications**:
- T175: Add threading.Lock() to TaskManager.__init__()
- T206, T231, T236, T241, T282, T287, T292, T297: Use `with self.lock:` for all task access
- T335-T341: Use Queue() for thread-safe notifications (no manual locking)
- T314: ReminderThread uses daemon=True for clean shutdown
- T416-T420: Thread safety testing tasks

**New Module Created**:
- **reminder_thread.py**: Background worker with ReminderThread class (T310-T332)
  - Extends threading.Thread with daemon=True
  - Checks reminders every 60 seconds with time.sleep(60)
  - Uses Queue for thread-safe notifications
  - Implements graceful shutdown with self.running flag

**Date Calculation Edge Cases** (documented in tasks):
- T189-T191: Monthly recurrence with calendar.monthrange() for month-end handling
- T382: Validate Jan 31 → Feb 28/29 edge case
- T397: Validate day 31 → day 30 for months with 30 days

**Parallel Opportunities**:
- Phase 1 & 2: US1 (recurring) and US2 (due dates) can develop in parallel (47 + 50 = 97 tasks)
- Phase 6: 10 tasks can run in parallel (docstrings, README sections)
- After Phase 0: US1/US2 can parallelize, US3 follows sequentially

**Implementation Strategies Documented**:
1. **MVP First**: Phase 0 + Phase 1 (US1 only) → 55 tasks, ~3.5 hours
2. **Incremental**: Add one story at a time, validate independently
3. **Sequential**: Complete all phases in order → ~11 hours estimated
4. **Parallel Team**: 3 developers → ~6 hours estimated

**Detailed Task Specifications**: 5 detailed task breakdowns provided:
- T176: Extend add_task() with recurrence field
- T181: Implement set_recurrence() with type validation
- T186: Implement calculate_next_due_date() with month-end edge cases
- T193: Implement create_next_occurrence() with cloning strategy
- T310: Create reminder_thread.py module with ReminderThread class
- T322: Implement check_reminders() with 60-second loop and Queue notifications

**Validation Coverage**: 52 validation tasks (T369-T420)
- 18 acceptance scenario tests (6 per user story)
- 8 edge case tests
- 11 success criteria tests
- 5 thread safety tests
- 10 documentation tasks

## Outcome

- ✅ Impact: Advanced Level tasks complete - ready for implementation with 248 actionable tasks including background threading
- 🧪 Tests: Task format validation PASSED, User story mapping PASSED, Dependency analysis PASSED, Thread safety requirements PASSED
- 📁 Files: 1 file created (tasks.md with 248 tasks)
- 🔁 Next prompts: `/sp.implement` to execute all tasks with special attention to thread safety, then comprehensive validation
- 🧠 Reflection: Task breakdown maintains independence per user story while clearly specifying thread safety requirements. All tasks follow strict checklist format. New module (reminder_thread.py) creation documented with 23 tasks. Date calculation edge cases explicitly tested. Background thread lifecycle (start, run, check, stop) clearly defined. Parallel opportunities identified (US1 + US2 can develop concurrently). Ready for implementation with comprehensive thread safety guidance.

## Evaluation notes (flywheel)

- Failure modes observed: None - task generation comprehensive with user-provided examples and thread safety requirements
- Graders run and results (PASS/FAIL): Task format validation - PASS (all 248 tasks follow checklist format), User story mapping - PASS (all 3 advanced stories covered with 18 acceptance scenarios), Thread safety requirements - PASS (Lock and Queue usage documented)
- Prompt variant (if applicable): N/A (first task generation for advanced level)
- Next experiment (smallest change to try): Execute Phase 0 (data model + Lock), then implement US1 (recurring) and US2 (due dates) in parallel if possible, then US3 (reminders + thread) sequentially, validate thread safety with concurrent operations
