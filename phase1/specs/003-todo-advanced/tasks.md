---
description: "Task list for Console Todo App - Advanced Level implementation"
---

# Tasks: Console Todo App - Advanced Level

**Input**: Design documents from `phase1/specs/003-todo-advanced/`
**Prerequisites**: plan.md (completed), spec.md (completed), Intermediate Level (002-todo-intermediate) fully implemented

**Tests**: No automated tests in Phase I - manual validation only per plan.md.

**Organization**: Tasks are grouped by user story (after Phase 0) to enable independent implementation and testing of each advanced feature.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Project root**: `phase1/`
- **Source code**: `phase1/src/`
- **Documentation**: `phase1/` (README.md)

---

## Phase 0: Data Model Extension (Foundation for Advanced Features)

**Purpose**: Extend task data structure to support recurrence, due dates, reminders, and parent tracking - MUST be complete before ANY advanced feature implementation

**⚠️ CRITICAL**: All advanced features depend on this phase being complete

- [x] T173 Add threading import to phase1/src/task_manager.py
- [x] T174 Add calendar import to phase1/src/task_manager.py (for month-end calculations)
- [x] T175 Add threading.Lock to TaskManager.__init__() in phase1/src/task_manager.py
- [x] T176 Extend add_task() method to include recurrence field (default None) in phase1/src/task_manager.py
- [x] T177 Extend add_task() method to include due_date field (default None) in phase1/src/task_manager.py
- [x] T178 Extend add_task() method to include reminder field (default None) in phase1/src/task_manager.py
- [x] T179 Extend add_task() method to include parent_task_id field (default None) in phase1/src/task_manager.py
- [x] T180 Verify task dictionary structure includes all 11 fields (id, title, description, completed, priority, tags, created_at, recurrence, due_date, reminder, parent_task_id)

**Checkpoint**: Data model extended - task creation now includes recurrence, due_date, reminder, and parent_task_id with None defaults

---

## Phase 1: User Story 1 - Recurring Tasks (Priority: P1) 🎯 High Impact

**Goal**: Users can create tasks that automatically repeat on a schedule (daily/weekly/monthly)

**Independent Test**: Create daily recurring task "Team standup", mark complete, verify next occurrence created for tomorrow with same title/priority/tags but fresh completion status

### Implementation for User Story 1 - Recurrence Management

- [x] T181 [US1] Implement set_recurrence(task_id, type, interval, days) method in phase1/src/task_manager.py
- [x] T182 [US1] Add recurrence type validation in set_recurrence() (must be "daily", "weekly", "monthly", or "none")
- [x] T183 [US1] Store recurrence as dict {"type": str, "interval": int, "days": list[str]} in set_recurrence()
- [x] T184 [US1] Return None from set_recurrence() if task not found or type invalid
- [x] T185 [US1] Add docstring to set_recurrence() method with type hints

### Implementation for User Story 1 - Next Occurrence Logic

- [x] T186 [US1] Implement calculate_next_due_date(task) method in phase1/src/task_manager.py
- [x] T187 [US1] Add daily recurrence logic in calculate_next_due_date() (current_due + interval days)
- [x] T188 [US1] Add weekly recurrence logic in calculate_next_due_date() (current_due + interval weeks)
- [x] T189 [US1] Add monthly recurrence logic in calculate_next_due_date() (handle month-end edge cases)
- [x] T190 [US1] Use calendar.monthrange() to get last day of target month in calculate_next_due_date()
- [x] T191 [US1] Use min(current_day, last_day_of_month) to handle day 31 → shorter months
- [x] T192 [US1] Add docstring to calculate_next_due_date() method with type hints

### Implementation for User Story 1 - Clone Task on Completion

- [x] T193 [US1] Implement create_next_occurrence(task_id) method in phase1/src/task_manager.py
- [x] T194 [US1] Check if task has recurrence in create_next_occurrence() (return None if not)
- [x] T195 [US1] Call calculate_next_due_date() to get next due date in create_next_occurrence()
- [x] T196 [US1] Clone task with new ID using _generate_id() in create_next_occurrence()
- [x] T197 [US1] Set completed=False for new occurrence in create_next_occurrence()
- [x] T198 [US1] Copy title, description, priority, tags from original in create_next_occurrence()
- [x] T199 [US1] Copy recurrence and reminder dicts using .copy() in create_next_occurrence()
- [x] T200 [US1] Set parent_task_id to original task ID in create_next_occurrence()
- [x] T201 [US1] Set created_at to current timestamp in create_next_occurrence()
- [x] T202 [US1] Append new task to self.tasks list in create_next_occurrence()
- [x] T203 [US1] Return new task dictionary from create_next_occurrence()
- [x] T204 [US1] Add docstring to create_next_occurrence() method with type hints

### Integration for User Story 1 - Auto-Create on Complete

- [x] T205 [US1] Modify toggle_complete() method to check for recurrence in phase1/src/task_manager.py
- [x] T206 [US1] Add thread-safe lock (with self.lock:) around toggle_complete() task access
- [x] T207 [US1] Call create_next_occurrence() when completing recurring task in toggle_complete()
- [x] T208 [US1] Return dict with {"current": task, "next": next_task} from toggle_complete()
- [x] T209 [US1] Update toggle_complete_flow() to handle recurring task response in phase1/src/main.py
- [x] T210 [US1] Display message "Next occurrence created: Task #X due [date]" in toggle_complete_flow()

### CLI Integration for User Story 1

- [x] T211 [US1] Implement set_recurrence_flow(manager) function in phase1/src/main.py
- [x] T212 [US1] Add task ID input prompt in set_recurrence_flow()
- [x] T213 [US1] Add recurrence type menu in set_recurrence_flow() (1=Daily, 2=Weekly, 3=Monthly, 4=None)
- [x] T214 [US1] Add interval input prompt in set_recurrence_flow() (default 1)
- [x] T215 [US1] Add days input for weekly recurrence in set_recurrence_flow() (comma-separated: mon,wed,fri)
- [x] T216 [US1] Add error handling for invalid task ID in set_recurrence_flow()
- [x] T217 [US1] Add error handling for invalid recurrence type in set_recurrence_flow()
- [x] T218 [US1] Add success message showing recurrence indicator in set_recurrence_flow()

### Display Updates for User Story 1

- [x] T219 [US1] Update view_tasks_flow() to display recurrence indicator in phase1/src/main.py
- [x] T220 [US1] Format recurrence display as "Recurring: Daily" or "Recurring: Weekly (Mon, Wed)"
- [x] T221 [US1] Add recurrence indicator after task description in display

### Delete Handling for User Story 1

- [x] T222 [US1] Update delete_task_flow() to check if task has recurrence in phase1/src/main.py
- [x] T223 [US1] Add prompt "Delete all future occurrences? (y/n)" for recurring tasks in delete_task_flow()
- [x] T224 [US1] If user answers "y", set recurrence to None before deleting in delete_task_flow()

### Menu Integration for User Story 1

- [x] T225 [US1] Update display_menu() to add option "11. Set Recurrence"
- [x] T226 [US1] Update get_user_choice() to validate choices "1-16" (Exit becomes option 16)
- [x] T227 [US1] Add route for choice "11" to call set_recurrence_flow() in main() event loop

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create recurring tasks that auto-generate next occurrences

---

## Phase 2: User Story 2 - Due Dates & Deadlines (Priority: P2)

**Goal**: Users can set due dates and see countdowns/overdue indicators

**Independent Test**: Set due date "2026-01-03 09:00" on task, verify displays "Due: Jan 3, 2026 9:00 AM (in 2 days)" with countdown

### Implementation for User Story 2 - Due Date Management

- [x] T228 [US2] Implement set_due_date(task_id, due_date) method in phase1/src/task_manager.py
- [x] T229 [US2] Add future date validation in set_due_date() (due_date > datetime.now())
- [x] T230 [US2] Return None if due date is in past in set_due_date()
- [x] T231 [US2] Add thread-safe lock around task access in set_due_date()
- [x] T232 [US2] Store due_date as datetime object in set_due_date()
- [x] T233 [US2] Add docstring to set_due_date() method with type hints

### Implementation for User Story 2 - Overdue & Upcoming

- [x] T234 [US2] Implement get_overdue_tasks() method in phase1/src/task_manager.py
- [x] T235 [US2] Filter tasks where due_date < now and not completed in get_overdue_tasks()
- [x] T236 [US2] Add thread-safe lock around task list access in get_overdue_tasks()
- [x] T237 [US2] Return sorted by due_date (earliest first) from get_overdue_tasks()
- [x] T238 [US2] Add docstring to get_overdue_tasks() method with type hints
- [x] T239 [US2] Implement get_upcoming_tasks(days) method in phase1/src/task_manager.py
- [x] T240 [US2] Filter tasks where now < due_date < now + days in get_upcoming_tasks()
- [x] T241 [US2] Add thread-safe lock around task list access in get_upcoming_tasks()
- [x] T242 [US2] Return sorted by due_date from get_upcoming_tasks()
- [x] T243 [US2] Add docstring to get_upcoming_tasks() method with type hints

### CLI Integration for User Story 2

- [x] T244 [US2] Implement set_due_date_flow(manager) function in phase1/src/main.py
- [x] T245 [US2] Add task ID input prompt in set_due_date_flow()
- [x] T246 [US2] Add due date input prompt (YYYY-MM-DD HH:MM format) in set_due_date_flow()
- [x] T247 [US2] Parse date string using datetime.strptime() in set_due_date_flow()
- [x] T248 [US2] Add error handling for invalid date format in set_due_date_flow()
- [x] T249 [US2] Add error handling for past date in set_due_date_flow()
- [x] T250 [US2] Display confirmation with human-readable date in set_due_date_flow()
- [x] T251 [US2] Implement view_overdue_flow(manager) function in phase1/src/main.py
- [x] T252 [US2] Call manager.get_overdue_tasks() in view_overdue_flow()
- [x] T253 [US2] Display count "Overdue Tasks: X" in view_overdue_flow()
- [x] T254 [US2] Display tasks with red/bold emphasis for overdue in view_overdue_flow()
- [x] T255 [US2] Calculate and display overdue duration in view_overdue_flow()
- [x] T256 [US2] Implement view_upcoming_flow(manager) function in phase1/src/main.py
- [x] T257 [US2] Call manager.get_upcoming_tasks(7) in view_upcoming_flow()
- [x] T258 [US2] Display count "Upcoming Tasks (next 7 days): X" in view_upcoming_flow()
- [x] T259 [US2] Display tasks with countdown display in view_upcoming_flow()

### Display Updates for User Story 2

- [x] T260 [US2] Create format_due_date_countdown(due_date) helper function in phase1/src/main.py
- [x] T261 [US2] Calculate delta between due_date and now in format_due_date_countdown()
- [x] T262 [US2] Return "in X days" or "in X hours" for future dates in format_due_date_countdown()
- [x] T263 [US2] Return "OVERDUE by X days/hours" for past dates in format_due_date_countdown()
- [x] T264 [US2] Add ANSI red color code for overdue text (\033[91m...\033[0m) in format_due_date_countdown()
- [x] T265 [US2] Update view_tasks_flow() to display due dates with countdown in phase1/src/main.py
- [x] T266 [US2] Display due date on separate line below task title in view_tasks_flow()

### Filter & Sort Updates for User Story 2

- [x] T267 [US2] Update filter_tasks_flow() to add "overdue" filter option in phase1/src/main.py
- [x] T268 [US2] Update filter_tasks_flow() to add "due_today" filter option in phase1/src/main.py
- [x] T269 [US2] Update filter_tasks_flow() to add "due_this_week" filter option in phase1/src/main.py
- [x] T270 [US2] Update sort_tasks_flow() to add "due date (earliest first)" sort option in phase1/src/main.py
- [x] T271 [US2] Update sort_tasks() method to handle "due_date" sort criteria in phase1/src/task_manager.py

### Menu Integration for User Story 2

- [x] T272 [US2] Update display_menu() to add option "12. Set Due Date"
- [x] T273 [US2] Update display_menu() to add option "14. View Overdue Tasks"
- [x] T274 [US2] Update display_menu() to add option "15. View Upcoming (7 days)"
- [x] T275 [US2] Add route for choice "12" to call set_due_date_flow() in main() event loop
- [x] T276 [US2] Add route for choice "14" to call view_overdue_flow() in main() event loop
- [x] T277 [US2] Add route for choice "15" to call view_upcoming_flow() in main() event loop

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 3: User Story 3 - Reminders (Priority: P3) - Data Layer

**Goal**: Store and manage reminder settings (offset + notified flag)

**Independent Test**: Set reminder "1hour" before due date, verify stored as {"offset_minutes": 60, "notified": false}

### Implementation for User Story 3 - Reminder Methods

- [x] T278 [US3] Implement set_reminder(task_id, offset_minutes) method in phase1/src/task_manager.py
- [x] T279 [US3] Add validation: task must have due_date in set_reminder()
- [x] T280 [US3] Return None if task has no due_date in set_reminder()
- [x] T281 [US3] Store reminder as dict {"offset_minutes": int, "notified": False} in set_reminder()
- [x] T282 [US3] Add thread-safe lock around task access in set_reminder()
- [x] T283 [US3] Add docstring to set_reminder() method with type hints
- [x] T284 [US3] Implement get_pending_reminders() method in phase1/src/task_manager.py
- [x] T285 [US3] Filter tasks with reminder where notified=False in get_pending_reminders()
- [x] T286 [US3] Filter tasks with due_date exists and not completed in get_pending_reminders()
- [x] T287 [US3] Add thread-safe lock around task list access in get_pending_reminders()
- [x] T288 [US3] Return list of tasks with pending reminders from get_pending_reminders()
- [x] T289 [US3] Add docstring to get_pending_reminders() method with type hints
- [x] T290 [US3] Implement mark_reminder_notified(task_id) method in phase1/src/task_manager.py
- [x] T291 [US3] Set task["reminder"]["notified"] = True in mark_reminder_notified()
- [x] T292 [US3] Add thread-safe lock around task access in mark_reminder_notified()
- [x] T293 [US3] Add docstring to mark_reminder_notified() method with type hints
- [x] T294 [US3] Implement snooze_reminder(task_id, minutes) method in phase1/src/task_manager.py
- [x] T295 [US3] Set reminder["notified"] = False in snooze_reminder()
- [x] T296 [US3] Update reminder["offset_minutes"] to new value in snooze_reminder()
- [x] T297 [US3] Add thread-safe lock around task access in snooze_reminder()
- [x] T298 [US3] Add docstring to snooze_reminder() method with type hints

### CLI Integration for User Story 3 - Reminder Setup

- [x] T299 [US3] Implement set_reminder_flow(manager) function in phase1/src/main.py
- [x] T300 [US3] Add task ID input prompt in set_reminder_flow()
- [x] T301 [US3] Check if task has due_date in set_reminder_flow() (error if not)
- [x] T302 [US3] Add reminder offset menu in set_reminder_flow() (1=15min, 2=1hour, 3=1day, 4=1week)
- [x] T303 [US3] Map user choice to offset_minutes in set_reminder_flow() (15, 60, 1440, 10080)
- [x] T304 [US3] Call manager.set_reminder() with offset in set_reminder_flow()
- [x] T305 [US3] Calculate and display reminder trigger time in set_reminder_flow()
- [x] T306 [US3] Add error handling for task without due date in set_reminder_flow()
- [x] T307 [US3] Add success message showing reminder offset in set_reminder_flow()

### Menu Integration for User Story 3 - Reminder Setup

- [x] T308 [US3] Update display_menu() to add option "13. Set Reminder"
- [x] T309 [US3] Add route for choice "13" to call set_reminder_flow() in main() event loop

**Checkpoint**: At this point, users can set reminders but background thread not yet running

---

## Phase 4: User Story 3 - Background Reminder Thread (Priority: P3)

**Goal**: Background thread checks reminders every 60 seconds and triggers notifications

**Independent Test**: Set reminder for 2 minutes from now, wait, verify notification appears in CLI with "⏰ REMINDER" message

### Create New Module: reminder_thread.py

- [x] T310 [US3] Create new file phase1/src/reminder_thread.py
- [x] T311 [US3] Add imports (threading, time, datetime, timedelta, Queue) to reminder_thread.py
- [x] T312 [US3] Create ReminderThread class extending threading.Thread in reminder_thread.py
- [x] T313 [US3] Add __init__(task_manager, notification_queue) to ReminderThread class
- [x] T314 [US3] Call super().__init__(daemon=True) in ReminderThread.__init__()
- [x] T315 [US3] Store task_manager and notification_queue as instance variables
- [x] T316 [US3] Add self.running = True flag for graceful shutdown
- [x] T317 [US3] Add docstring to ReminderThread class

### Implement Background Check Logic

- [x] T318 [US3] Implement run() method in ReminderThread class
- [x] T319 [US3] Add while loop with self.running check in run() method
- [x] T320 [US3] Call self.check_reminders() in each loop iteration
- [x] T321 [US3] Add time.sleep(60) to sleep between checks in run() method
- [x] T322 [US3] Implement check_reminders() method in ReminderThread class
- [x] T323 [US3] Get current time using datetime.now() in check_reminders()
- [x] T324 [US3] Call task_manager.get_pending_reminders() in check_reminders()
- [x] T325 [US3] Loop through pending reminders in check_reminders()
- [x] T326 [US3] Calculate reminder_time as (due_date - offset_minutes) for each task
- [x] T327 [US3] Check if now >= reminder_time for each task
- [x] T328 [US3] Put task in notification_queue if reminder time reached
- [x] T329 [US3] Call task_manager.mark_reminder_notified() after queueing notification
- [x] T330 [US3] Add error handling for date parsing in check_reminders()
- [x] T331 [US3] Implement stop() method to set self.running = False
- [x] T332 [US3] Add docstrings to run(), check_reminders(), stop() methods

### Integrate Background Thread in main.py

- [x] T333 [US3] Add Queue import to phase1/src/main.py (from queue import Queue)
- [x] T334 [US3] Add ReminderThread import to phase1/src/main.py (from reminder_thread import ReminderThread)
- [x] T335 [US3] Create notification_queue = Queue() in main() function
- [x] T336 [US3] Create reminder_thread = ReminderThread(manager, notification_queue) in main()
- [x] T337 [US3] Call reminder_thread.start() before event loop in main()
- [x] T338 [US3] Add notification queue check before display_menu() in main() event loop
- [x] T339 [US3] Use while not notification_queue.empty() to process all queued notifications
- [x] T340 [US3] Call notification_queue.get() to retrieve task for notification
- [x] T341 [US3] Call display_reminder_notification(task, manager) for each queued notification

### Implement Notification Display

- [x] T342 [US3] Implement display_reminder_notification(task, manager) function in phase1/src/main.py
- [x] T343 [US3] Display separator line "=" * 50 in display_reminder_notification()
- [x] T344 [US3] Display "⏰ REMINDER: '[task title]' is due soon!" message
- [x] T345 [US3] Calculate and display time until due (e.g., "due in 1 hour")
- [x] T346 [US3] Display separator line in display_reminder_notification()
- [x] T347 [US3] Add action prompt "(s)nooze 10min | (v)iew task | (c)ontinue" in display_reminder_notification()
- [x] T348 [US3] Handle snooze action: call manager.snooze_reminder(task_id, 10)
- [x] T349 [US3] Handle view action: display task details with format_task_display()
- [x] T350 [US3] Handle continue action: return to menu
- [x] T351 [US3] Add success message "Reminder snoozed for 10 minutes" for snooze action

### Display Updates for User Story 3

- [x] T352 [US3] Update view_tasks_flow() to display reminder status in phase1/src/main.py
- [x] T353 [US3] Format reminder display as "Reminder: 1 hour before" if not notified
- [x] T354 [US3] Format reminder display as "Reminder: Sent at [time]" if notified
- [x] T355 [US3] Add reminder info on separate line below due date in display

**Checkpoint**: All 3 user stories (US1-US3) should now be independently functional with background thread running

---

## Phase 5: Menu & Display Integration

**Purpose**: Final menu updates and display formatting polish

### Menu Updates

- [x] T356 Update display_menu() to change "Exit" to option "16" in phase1/src/main.py
- [x] T357 Update get_user_choice() final validation to accept "16" for Exit
- [x] T358 Update main() event loop to check for choice "16" for Exit
- [x] T359 Add separator or grouping for advanced options (11-15) in display_menu()

### Display Formatting Consolidation

- [x] T360 [P] Create format_task_full_display(task) helper combining all fields in phase1/src/main.py
- [x] T361 [P] Include priority indicator in format_task_full_display()
- [x] T362 [P] Include completion checkbox in format_task_full_display()
- [x] T363 [P] Include tags with # prefix in format_task_full_display()
- [x] T364 [P] Include due date with countdown in format_task_full_display()
- [x] T365 [P] Include recurrence indicator in format_task_full_display()
- [x] T366 [P] Include reminder status in format_task_full_display()
- [x] T367 [P] Include overdue emphasis (red text) in format_task_full_display()
- [x] T368 Update all display flows to use format_task_full_display() helper

**Checkpoint**: All menu options (1-16) work, all task fields display correctly

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, final validation, and deployment readiness

### Documentation

- [x] T369 [P] Add docstrings to all new functions in phase1/src/main.py (set_recurrence_flow, set_due_date_flow, set_reminder_flow, view_overdue_flow, view_upcoming_flow, display_reminder_notification)
- [x] T370 [P] Add docstrings to all new methods in phase1/src/task_manager.py (set_recurrence, calculate_next_due_date, create_next_occurrence, set_due_date, get_overdue_tasks, get_upcoming_tasks, set_reminder, get_pending_reminders, mark_reminder_notified, snooze_reminder)
- [x] T371 [P] Add module docstring to phase1/src/reminder_thread.py
- [x] T372 [P] Update phase1/README.md with advanced features section
- [x] T373 [P] Add recurring tasks examples to phase1/README.md
- [x] T374 [P] Add due dates examples to phase1/README.md
- [x] T375 [P] Add reminders examples to phase1/README.md
- [x] T376 [P] Add threading note to phase1/README.md (background reminder thread)
- [x] T377 [P] Update data model in README showing all 11 fields
- [x] T378 [P] Update menu in README showing 16 options

### Validation - User Story 1 (Recurring Tasks)

- [x] T379 Validate acceptance scenario 1: Create daily recurring task, verify "Recurring: Daily" indicator
- [x] T380 Validate acceptance scenario 2: Mark daily recurring task complete, verify next created for tomorrow
- [x] T381 Validate acceptance scenario 3: Mark weekly recurring task (Monday) complete, verify next is Monday +7 days
- [x] T382 Validate acceptance scenario 4: Create monthly recurring on Jan 31, complete, verify next is Feb 28/29
- [x] T383 Validate acceptance scenario 5: Delete recurring task, verify prompt "Delete all future occurrences?"
- [x] T384 Validate acceptance scenario 6: Complete recurring task early, verify next based on original schedule

### Validation - User Story 2 (Due Dates)

- [x] T385 Validate acceptance scenario 1: Set future due date, verify displays "Due: Jan 3, 2026 9:00 AM"
- [x] T386 Validate acceptance scenario 2: View task with future due date, verify countdown "due in 2 days"
- [x] T387 Validate acceptance scenario 3: Let task become overdue, verify "OVERDUE by 3 hours" with red emphasis
- [x] T388 Validate acceptance scenario 4: Try to set past due date, verify error "Due date must be in the future"
- [x] T389 Validate acceptance scenario 5: Filter by overdue, verify only overdue tasks shown
- [x] T390 Validate acceptance scenario 6: Sort by due date, verify earliest due date first

### Validation - User Story 3 (Reminders)

- [x] T391 Validate acceptance scenario 1: Set reminder on task with due date, verify stored as {"offset_minutes": 60, "notified": false}
- [x] T392 Validate acceptance scenario 2: Wait for reminder time, verify "⏰ REMINDER" notification displays
- [x] T393 Validate acceptance scenario 3: Acknowledge reminder, verify marked as notified=true (no duplicates)
- [x] T394 Validate acceptance scenario 4: Snooze reminder, verify appears again in 10 minutes
- [x] T395 Validate acceptance scenario 5: View task with reminder, verify shows "Reminder: 1 hour before"
- [x] T396 Validate acceptance scenario 6: Try to set reminder without due date, verify error message

### Edge Cases Validation

- [x] T397 Validate edge case: Monthly recurrence on day 31, next month has 30 days (should use day 30)
- [x] T398 Validate edge case: Complete recurring task early (next should be based on original schedule)
- [x] T399 Validate edge case: Multiple reminders trigger simultaneously (should display in sequence)
- [x] T400 Validate edge case: Reminder for overdue task (should not notify)
- [x] T401 Validate edge case: Set due date to current minute (should immediately become overdue)
- [x] T402 Validate edge case: Background thread CPU usage (should be minimal with 60s sleep)
- [x] T403 Validate edge case: Weekly recurrence "Mon, Wed" - complete Monday (next should be Wednesday, 2 days later)
- [x] T404 Validate edge case: Exit app while reminder thread running (should stop cleanly with daemon)

### Success Criteria Validation

- [x] T405 Validate SC-023: Users can set recurring tasks in <10 seconds
- [x] T406 Validate SC-024: Completing recurring task creates next occurrence in <2 seconds
- [x] T407 Validate SC-025: Users can set due date and reminder in <15 seconds total
- [x] T408 Validate SC-026: Background reminder thread starts within 1 second of app launch
- [x] T409 Validate SC-027: Reminder notifications appear within 1 minute of scheduled time
- [x] T410 Validate SC-028: Overdue tasks are visually distinguished (red text or bold)
- [x] T411 Validate SC-029: Users can filter to see only overdue tasks in <3 seconds
- [x] T412 Validate SC-030: System handles 100+ recurring tasks without performance degradation
- [x] T413 Validate SC-031: Full advanced demo workflow completes in <90 seconds
- [x] T414 Validate SC-032: Zero crashes during normal operation with advanced features
- [x] T415 Validate SC-033: Reminder background thread runs continuously without blocking CLI

### Thread Safety Testing

- [x] T416 Test concurrent access: Add task while reminder thread checks (verify no race conditions)
- [x] T417 Test thread shutdown: Exit app while reminder thread running (verify clean stop)
- [x] T418 Test Lock usage: Verify all task list access uses with self.lock: pattern
- [x] T419 Test Queue usage: Verify notification queue is thread-safe (no manual locking)
- [x] T420 Test multiple reminders: Queue multiple notifications, verify all display correctly

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 0 (Data Model Extension)**: Depends on Intermediate Level (002-todo-intermediate) complete - BLOCKS all advanced features
- **Phase 1 (US1 - Recurring Tasks)**: Depends on Phase 0 - Can start after data model extended
- **Phase 2 (US2 - Due Dates)**: Depends on Phase 0 - Can run in parallel with Phase 1
- **Phase 3 (US3 - Reminders Data)**: Depends on Phase 0 and Phase 2 (needs due dates) - Sequential after Phase 2
- **Phase 4 (US3 - Background Thread)**: Depends on Phase 3 - Sequential after reminder methods
- **Phase 5 (Menu Integration)**: Depends on Phases 1, 2, 3 complete - Integrates all features
- **Phase 6 (Polish)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1 - Recurring Tasks)**: Can start after Phase 0 - Independent of US2 and US3
- **User Story 2 (P2 - Due Dates)**: Can start after Phase 0 - Independent of US1, required by US3
- **User Story 3 (P3 - Reminders)**: Depends on Phase 0 and US2 (needs due dates for reminders)

### Within Each User Story

- US1: set_recurrence() → calculate_next_due_date() → create_next_occurrence() → modify toggle_complete() → CLI flows → display updates → delete handling → menu
- US2: set_due_date() → get_overdue/upcoming() → CLI flows → display updates → filter/sort integration → menu
- US3: set_reminder() → get_pending_reminders() → mark_notified/snooze → ReminderThread class → integrate in main() → notification display → menu

### Parallel Opportunities

- **Phase 0 (Data Model)**: T173-T180 must run sequentially (same file modifications)
- **Phase 1 & 2**: Can run in parallel (US1 and US2 are independent)
- **Phase 6 (Polish)**: T369-T378 can run in parallel (docstrings and README sections)
- **Between User Stories**: Once Phase 0 complete, US1 and US2 can be worked on in parallel, US3 follows after US2

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 0: Data Model Extension (T173-T180)
2. Complete Phase 1: User Story 1 - Recurring Tasks (T181-T227)
3. **STOP and VALIDATE**: Manually test US1 acceptance scenarios
4. Demo recurring task functionality

**Minimal Deliverable**: After completing through Phase 1, you have recurring tasks that auto-generate next occurrences - a valuable productivity feature.

### Incremental Delivery

1. Complete Phase 0 (T173-T180) → Data model extended
2. Add User Story 1 (T181-T227) → Test independently → **Deploy/Demo with recurring tasks!**
3. Add User Story 2 (T228-T277) → Test independently → Deploy/Demo (now with due dates)
4. Add User Story 3 (T278-T355) → Test independently → Deploy/Demo (full advanced features with reminders)
5. Complete Menu Integration (T356-T368) → All features unified
6. Complete Polish (T369-T420) → Final validation → **Production ready!**

Each story adds value without breaking previous stories.

### Sequential Strategy (Single Developer)

Recommended order:
1. Phase 0: Data Model Extension → 20 minutes
2. Phase 1: User Story 1 (Recurring Tasks) → 3 hours
3. Phase 2: User Story 2 (Due Dates) → 2 hours
4. Phase 3: User Story 3 (Reminders Data) → 1 hour
5. Phase 4: User Story 3 (Background Thread) → 2 hours
6. Phase 5: Menu Integration → 1 hour
7. Phase 6: Polish & Validation → 2 hours

**Total estimated time**: ~11 hours for complete advanced implementation

### Parallel Team Strategy

With multiple developers:

1. Team completes Phase 0 together (T173-T180) → 20 minutes
2. Parallelize Phase 1 and Phase 2:
   - Developer A: User Story 1 - Recurring Tasks (T181-T227) → 3 hours
   - Developer B: User Story 2 - Due Dates (T228-T277) → 2 hours
3. Developer C: User Story 3 - Reminders (T278-T355) → 3 hours (after US2 complete)
4. Team: Menu Integration (T356-T368) → 1 hour
5. All developers: Polish together (T369-T420) → 2 hours

**Total elapsed time with 3 developers**: ~6 hours

---

## Task Details

### T176: Extend add_task() for Recurrence Field

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Modify add_task() method (currently at lines 71-81)
- Add `"recurrence": None` to task dictionary
- Maintain existing fields

**Implementation Location**: task_manager.py:71-81

**Type Signature**: No change to method signature

**Links**: [spec.md FR-031], [plan.md Phase 0]

---

### T181: Implement set_recurrence() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int), type (str), interval (int, default=1), days (list[str], optional)
- Validate type is one of: "daily", "weekly", "monthly", "none"
- If type is "none", set recurrence to None
- Otherwise, store as dict: `{"type": type, "interval": interval, "days": days or []}`
- Use thread-safe lock: `with self.lock:` around task access

**Type Signature**: `def set_recurrence(self, task_id: int, type: str, interval: int = 1, days: Optional[list[str]] = None) -> Optional[dict]`

**Links**: [spec.md FR-031, FR-032, FR-033], [plan.md Decision 1]

---

### T186: Implement calculate_next_due_date() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task (dict) parameter
- Extract recurrence dict and current due_date (or datetime.now() if None)
- Based on recurrence["type"]:
  - **daily**: return current_due + timedelta(days=interval)
  - **weekly**: return current_due + timedelta(weeks=interval)
  - **monthly**:
    - Calculate next_month = current.month + interval
    - Calculate year with overflow: `year = current.year + (next_month - 1) // 12`
    - Calculate month with modulo: `month = (next_month - 1) % 12 + 1`
    - Get last day of target month: `last_day = calendar.monthrange(year, month)[1]`
    - Use min: `day = min(current.day, last_day)` (handles day 31 → 28/29/30)
    - Return current_due.replace(year=year, month=month, day=day)
- Import needed: `from datetime import timedelta` and `import calendar`

**Type Signature**: `def calculate_next_due_date(self, task: dict) -> datetime`

**Links**: [spec.md FR-038], [plan.md Decision 1, Risk 2]

---

### T193: Implement create_next_occurrence() Method

**File**: `phase1/src/task_manager.py`

**Functionality**:
- Accept task_id (int) parameter
- Get task using get_task(task_id)
- Return None if task not found or no recurrence
- Call calculate_next_due_date(task) to get next due date
- Create new task dict with:
  - `id`: self._generate_id()
  - `title`, `description`, `priority`: copy from original
  - `tags`: task["tags"].copy() (shallow copy of list)
  - `recurrence`: task["recurrence"].copy() (shallow copy of dict)
  - `reminder`: task["reminder"].copy() if exists else None
  - `completed`: False (RESET)
  - `due_date`: next_due (calculated value)
  - `parent_task_id`: task_id (link to original)
  - `created_at`: datetime.now().isoformat()
- Append new task to self.tasks
- Return new task
- Use thread-safe lock: `with self.lock:` around task list append

**Type Signature**: `def create_next_occurrence(self, task_id: int) -> Optional[dict]`

**Links**: [spec.md FR-034, FR-035, FR-036, FR-037], [plan.md Decision 1]

---

### T310: Create reminder_thread.py Module

**File**: `phase1/src/reminder_thread.py` (NEW FILE)

**Functionality**:
- Create new Python module file
- Add imports:
  ```python
  import threading
  import time
  from datetime import datetime, timedelta
  from queue import Queue
  from typing import TYPE_CHECKING

  if TYPE_CHECKING:
      from task_manager import TaskManager
  ```
- Create ReminderThread class extending threading.Thread
- Add module docstring explaining background reminder checking

**Type Signature**: Class definition

**Links**: [spec.md FR-053], [plan.md Component 3, Decision 2, Decision 3]

---

### T322: Implement check_reminders() Method

**File**: `phase1/src/reminder_thread.py`

**Functionality**:
- Get current time: `now = datetime.now()`
- Call `self.task_manager.get_pending_reminders()` (uses lock internally)
- Loop through each task with pending reminder
- For each task:
  - Parse due_date from ISO string if needed
  - Calculate reminder_time = due_date - timedelta(minutes=offset_minutes)
  - Check if now >= reminder_time
  - If yes:
    - Put task in self.notification_queue (thread-safe Queue)
    - Call self.task_manager.mark_reminder_notified(task["id"])
- Handle any date parsing errors gracefully (skip task on error)

**Type Signature**: `def check_reminders(self) -> None`

**Links**: [spec.md FR-053, FR-054, FR-055], [plan.md Decision 2, Decision 3]

---

## Notes

- **[P] tasks** = different files/sections, no dependencies - can run in parallel
- **[Story] label** = maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group of tasks
- Stop at any checkpoint to validate story independently
- **No automated tests in Phase I** - manual validation only (per plan.md)
- Type hints required on all new methods (per constitution Code Quality standards)
- Zero external dependencies - Python stdlib only (threading, datetime, calendar, queue)
- **Thread safety**: All task list access must use `with self.lock:` pattern
- **Daemon thread**: Use `daemon=True` so background thread stops with main app
- **Avoid**: race conditions, blocking operations in background thread, missing lock usage

## Validation Checklist

After completing all tasks, verify:

- [ ] All 3 advanced user stories work per acceptance scenarios (spec.md)
- [ ] All 28 new functional requirements met (FR-031 through FR-058)
- [ ] All 11 new success criteria met (SC-023 through SC-033)
- [ ] All edge cases handled (8 cases: month-end, early completion, multiple reminders, etc.)
- [ ] Code follows Python PEP 8 style
- [ ] Type hints on all new methods
- [ ] Docstrings on all new functions
- [ ] Thread-safe operations (Lock + Queue usage correct)
- [ ] Background thread runs without blocking CLI
- [ ] README.md documents all 10 features (5 Basic + 3 Intermediate + 2 Advanced)
- [ ] Advanced demo workflow completes in <90 seconds
- [ ] Zero crashes during normal operation with advanced features
- [ ] Works with 100+ recurring tasks without degradation

## Next Steps

After completing tasks.md:
1. Run `/sp.implement` to execute all tasks sequentially
2. Perform manual validation against checklist above
3. Test background reminder thread thoroughly
4. Create demo video (<90 seconds showing all 10 features)
5. Update README.md with comprehensive advanced examples
6. Commit to git with message: "feat: add recurring tasks, due dates, and reminders to Phase I console app"
7. Proceed to Phase II planning (web application with persistence)
