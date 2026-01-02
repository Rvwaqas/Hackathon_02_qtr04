# Feature Specification: Console Todo App - Advanced Level

**Feature Branch**: `003-todo-advanced`
**Created**: 2025-12-31
**Status**: Draft
**Input**: User description: "Phase I: Todo Console App (Advanced Level) - Add recurring tasks and due date reminders with background notifications"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recurring Tasks (Priority: P1) 🎯 High Impact

As a user, I can create tasks that automatically repeat on a schedule so that I don't have to manually recreate routine tasks.

**Why this priority**: Recurring tasks are fundamental to productivity - many users have daily standups, weekly reports, monthly reviews that repeat indefinitely. This is the core advanced feature that distinguishes power users from casual users.

**Independent Test**: Create a daily recurring task "Team standup", mark it complete, verify a new occurrence is automatically created for the next day with the same title, priority, and tags but fresh completion status.

**Acceptance Scenarios**:

1. **Given** I'm creating a new task, **When** I set recurrence to "daily" with interval 1, **Then** task displays "Recurring: Daily" indicator
2. **Given** I have a recurring task "Team standup" set to daily, **When** I mark it complete, **Then** system automatically creates next occurrence for tomorrow with same title/priority/tags but pending status
3. **Given** I have a weekly recurring task on Mondays, **When** I mark it complete, **Then** next occurrence is created for next Monday (7 days later)
4. **Given** I have a monthly recurring task on day 31, **When** completing it in January (31 days), **Then** next occurrence for February uses day 28/29 (last day of month)
5. **Given** I want to delete a recurring task, **When** I choose delete, **Then** system prompts "Delete all future occurrences? (y/n)"
6. **Given** I complete a recurring task 2 days early, **When** next occurrence is created, **Then** due date is still based on original schedule (not adjusted for early completion)

---

### User Story 2 - Due Dates & Deadlines (Priority: P2)

As a user, I can set due dates on tasks so that I know when work needs to be completed and can prioritize accordingly.

**Why this priority**: Due dates enable time management and prioritization. Without them, users can't distinguish urgent from non-urgent tasks. This must come after recurring tasks to support recurring tasks with due dates.

**Independent Test**: Create task "Submit report", set due date to "2026-01-03 09:00", verify task displays "Due: Jan 3, 2026 9:00 AM" and shows countdown "in 3 days" (if today is Dec 31).

**Acceptance Scenarios**:

1. **Given** I'm creating or updating a task, **When** I enter due date "2026-01-03 09:00", **Then** task displays "Due: Jan 3, 2026 9:00 AM" in human-readable format
2. **Given** I have a task with due date in the future, **When** viewing tasks, **Then** task shows countdown like "due in 2 days" or "due in 3 hours"
3. **Given** I have a task with due date in the past, **When** viewing tasks, **Then** task shows "OVERDUE by 3 hours" or "OVERDUE by 2 days" with visual emphasis
4. **Given** I try to set due date to a past date/time, **When** submitting, **Then** system shows error "Due date must be in the future"
5. **Given** I want to filter by due date, **When** I use filter menu, **Then** I can filter by "overdue", "due_today", "due_this_week"
6. **Given** I want to sort by urgency, **When** I choose sort by due date, **Then** tasks are ordered earliest due date first

---

### User Story 3 - Reminders & Notifications (Priority: P3)

As a user, I can set reminders before due dates so that I receive timely notifications and don't miss deadlines.

**Why this priority**: Reminders close the loop on due dates by proactively notifying users. Depends on due dates (US2) being implemented first. While valuable, users can still manually check due dates without this automation.

**Independent Test**: Create task with due date tomorrow at 2pm, set reminder for 1 hour before, wait until tomorrow at 1pm, verify CLI displays "⏰ REMINDER: [task title] is due in 1 hour!" notification.

**Acceptance Scenarios**:

1. **Given** I have a task with a due date, **When** I set reminder to "1hour" before due, **Then** reminder is stored as 60 minutes offset with notified=false
2. **Given** reminder time is reached, **When** background thread detects it, **Then** CLI displays "⏰ REMINDER: '[task title]' is due in 1 hour!" notification
3. **Given** reminder notification is shown, **When** I press Enter to continue, **Then** reminder is marked as notified=true to prevent duplicates
4. **Given** reminder notification is shown, **When** I choose snooze option, **Then** reminder is rescheduled for 10 minutes later with notified=false
5. **Given** I want to view a task with a reminder, **When** viewing task details, **Then** task shows "Reminder: 1 hour before" or "Reminder: Sent at 1:00 PM" if already notified
6. **Given** I set reminder on task without due date, **When** submitting, **Then** system shows error "Cannot set reminder on task without due date"

---

### Edge Cases

- What happens when user sets monthly recurrence on day 31 and next month has only 30 days? → System uses day 30 (last day of month)
- What happens when user completes recurring task 2 days early? → Next occurrence still based on original schedule (not completion date)
- What happens when user deletes recurring task? → System prompts "Delete all future occurrences? (y/n)" - if yes, marks as non-recurring before delete
- What happens when reminder notification is shown but user exits app? → Notification lost (in-memory only), will reappear on next app launch if reminder time still valid
- What happens when user sets due date to exactly now (current minute)? → Accepted, shows "due in 0 minutes", immediately becomes overdue after 1 minute
- What happens when background thread checks reminders every 1 minute and reminder offset is 15 minutes? → Notification may trigger between 14-15 minutes before due (acceptable precision loss)
- What happens when user has 10 overdue reminders? → All display in sequence when app starts, user must acknowledge each
- What happens when user sets weekly recurrence for "Monday, Wednesday" and completes Monday's task? → System creates next occurrence for Wednesday (2 days later), not next Monday

## Requirements *(mandatory)*

### Functional Requirements

**Existing Requirements (from Basic + Intermediate Levels)**:
- FR-001 through FR-030: All existing requirements from Basic and Intermediate levels remain unchanged

**New Requirements (Advanced Level)**:

#### Recurring Tasks (F9)

- **FR-031**: System MUST support recurrence types: "daily", "weekly", "monthly", "none" (default)
- **FR-032**: System MUST allow users to set recurrence during task creation or via update
- **FR-033**: System MUST store recurrence rules as: `{"type": str, "interval": int, "days": list[str]}`
- **FR-034**: System MUST automatically create next occurrence when recurring task is marked complete
- **FR-035**: Next occurrence MUST inherit: title, description, priority, tags from original task
- **FR-036**: Next occurrence MUST NOT inherit: completion status (always starts as pending)
- **FR-037**: Next occurrence MUST get new unique ID and link to parent via parent_task_id
- **FR-038**: System MUST calculate next due date based on recurrence type:
  - Daily: current_due + (interval × 1 day)
  - Weekly: current_due + (interval × 7 days) OR specific weekday
  - Monthly: current_due + (interval × 1 month), adjust day if month is shorter
- **FR-039**: System MUST display recurrence indicator: "Recurring: Daily", "Recurring: Weekly (Mon, Wed)", "Recurring: Monthly"
- **FR-040**: System MUST prompt "Delete all future occurrences? (y/n)" when deleting recurring task
- **FR-041**: If user answers "yes" to delete prompt, system MUST mark task as non-recurring (type="none") before deletion

#### Due Dates (F10a)

- **FR-042**: System MUST allow users to set due date in format "YYYY-MM-DD HH:MM"
- **FR-043**: System MUST display due dates in human-readable format: "Due: Jan 3, 2026 9:00 AM"
- **FR-044**: Due date MUST be optional (None/null if not set)
- **FR-045**: System MUST validate due date is in the future (not past)
- **FR-046**: System MUST calculate and display countdown: "due in 2 days", "due in 3 hours"
- **FR-047**: System MUST calculate and display overdue duration: "OVERDUE by 3 hours", "OVERDUE by 2 days"
- **FR-048**: System MUST visually emphasize overdue tasks (bold text or special marker)
- **FR-049**: System MUST provide filter options: "overdue", "due_today", "due_this_week"
- **FR-050**: System MUST provide sort option: "due_date" (earliest first)

#### Reminders (F10b)

- **FR-051**: System MUST allow users to set reminder offset: "15min", "1hour", "1day", "1week" before due date
- **FR-052**: System MUST store reminder as: `{"offset_minutes": int, "notified": bool}`
- **FR-053**: System MUST run background thread that checks reminders every 1 minute
- **FR-054**: System MUST display CLI notification when reminder time reached: "⏰ REMINDER: '[task]' is due in [time]!"
- **FR-055**: System MUST mark reminder as notified=true after displaying to prevent duplicates
- **FR-056**: System MUST provide snooze option: "Remind again in 10 minutes"
- **FR-057**: System MUST NOT allow reminder on task without due date
- **FR-058**: System MUST show reminder status in task view: "Reminder: 1 hour before" or "Reminder: Sent at 1:00 PM"

### Key Entities

- **Task** (updated from Intermediate level):
  - `id` (integer): Unique auto-incrementing identifier
  - `title` (string, required): Task name (1-200 chars)
  - `description` (string, optional): Extended details (max 1000 chars)
  - `completed` (boolean): Status indicator (default False)
  - `priority` (string): Priority level - "high", "medium", "low", "none" (default "none")
  - `tags` (list of strings): Category tags (0-5 tags, each 1-20 chars, alphanumeric, lowercase)
  - `created_at` (datetime): Timestamp of creation
  - **NEW - Advanced Fields**:
    - `recurrence` (dict or None): Recurrence rules `{"type": str, "interval": int, "days": list[str]}` (default None)
    - `due_date` (datetime or None): When task is due (default None)
    - `reminder` (dict or None): Reminder settings `{"offset_minutes": int, "notified": bool}` (default None)
    - `parent_task_id` (integer or None): Links to original recurring task (default None)

## Success Criteria *(mandatory)*

### Measurable Outcomes

**Existing Criteria (from Basic + Intermediate Levels)**:
- SC-001 through SC-022: All existing success criteria from Basic and Intermediate levels remain

**New Criteria (Advanced Level)**:

- **SC-023**: Users can set recurring tasks in <10 seconds
- **SC-024**: Completing recurring task automatically creates next occurrence in <2 seconds
- **SC-025**: Users can set due date and reminder in <15 seconds total
- **SC-026**: Background reminder thread starts within 1 second of app launch
- **SC-027**: Reminder notifications appear within 1 minute of scheduled reminder time (60-second precision acceptable)
- **SC-028**: Overdue tasks are visually distinguished from non-overdue tasks
- **SC-029**: Users can filter to see only overdue tasks in <3 seconds
- **SC-030**: System handles 100+ recurring tasks without performance degradation
- **SC-031**: Full advanced demo workflow (create recurring task with due date + reminder, complete it, see next occurrence, receive reminder) completes in <90 seconds
- **SC-032**: Zero crashes during normal operation with advanced features
- **SC-033**: Reminder background thread runs continuously without blocking CLI interactions

## Assumptions

1. **Existing Implementation**: Intermediate Level (002-todo-intermediate) is fully implemented and working with priorities, tags, search, filter, and sort
2. **Code Reuse**: Will extend existing TaskManager and main.py rather than rewriting
3. **Backward Compatibility**: Existing tasks without recurrence/due_date/reminder will default to None values
4. **User Environment**: Users have Python 3.13+ with threading support (stdlib)
5. **Reminder Precision**: 1-minute check interval is acceptable precision (reminder may trigger 0-59 seconds late)
6. **CLI Notifications**: Notifications displayed in terminal only (no OS-level popups, email, or SMS)
7. **In-Memory Limitations**: Reminders lost if app exits before notification time (acceptable for Phase I)
8. **Timezone**: All dates/times use local system timezone (no timezone conversion)
9. **Recurrence Start Date**: For recurring tasks, if no due date set, recurrence starts from created_at timestamp
10. **Monthly Edge Cases**: Monthly recurrence on day 29-31 will use last day of shorter months (e.g., Feb 28/29)

## Out of Scope

The following are explicitly NOT included in Advanced Level (Phase I):

- Persistent storage (file/database) - deferred to Phase II
- User authentication/multiple users - deferred to Phase II
- Email or SMS notifications - CLI notifications only
- OS-level notifications (system tray, desktop popups) - CLI only
- Calendar integration (Google Calendar, Outlook) - standalone app
- Task dependencies or subtasks - future enhancement
- Natural language date parsing ("tomorrow", "next Monday") - use ISO format only
- Timezone support - local system timezone only
- Snooze presets (custom snooze duration) - fixed 10-minute snooze only
- Multiple reminder types (email + CLI) - CLI only
- Recurring task series management (edit all future occurrences) - each occurrence is independent after creation
- Reminder history/log - notified flag only, no history tracking
- Background process as system service - thread within app process only

## Implementation Notes

This advanced spec builds on the existing intermediate implementation (002-todo-intermediate). The implementation approach should:

1. **Extend Data Model**: Add recurrence, due_date, reminder, parent_task_id fields to task dictionary
2. **Add Background Thread**: Create ReminderThread class that runs continuously and checks reminders every 60 seconds
3. **Extend TaskManager**: Add methods for set_recurrence(), set_due_date(), set_reminder(), create_next_occurrence(), get_overdue_tasks(), get_upcoming_tasks()
4. **Extend CLI**: Add new menu options (11-15) and corresponding flow functions
5. **Update Display**: Modify view_tasks_flow() to show recurrence indicators, due dates, countdowns, and overdue emphasis
6. **Handle Recurring Logic**: When marking recurring task complete, check if has recurrence, calculate next due date, create new task, link via parent_task_id
7. **Date Calculations**: Use datetime and dateutil (stdlib relativedelta) for date arithmetic
8. **Thread Safety**: Use threading.Lock for accessing shared task list from background thread
9. **Graceful Shutdown**: Ensure reminder thread stops cleanly when app exits

## Dependencies

- **Requires**: Spec 002-todo-intermediate (Intermediate Level) must be implemented and working
- **Blocks**: None - this is the final Phase I enhancement
- **Related**: Phase II will add persistence for recurring tasks, due dates, and reminders
