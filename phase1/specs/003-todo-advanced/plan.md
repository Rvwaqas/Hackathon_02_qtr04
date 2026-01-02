# Implementation Plan: Console Todo App - Advanced Level

**Feature Branch**: `003-todo-advanced`
**Created**: 2025-12-31
**Status**: Draft
**Input**: Spec 003-todo-advanced

## Technical Context

### Existing Foundation (From Basic + Intermediate Levels)
- **Implementation**: `phase1/src/task_manager.py` (308 lines) + `phase1/src/main.py` (569 lines)
- **Architecture**: 2-component design (UI layer + business logic layer)
- **Storage**: In-memory list of dictionaries
- **Current Task Schema**:
  ```python
  task = {
      "id": int,
      "title": str,
      "description": str,
      "completed": bool,
      "priority": str,  # "high" | "medium" | "low" | "none"
      "tags": list[str],  # 0-5 tags
      "created_at": str  # ISO format
  }
  ```

### Extension Approach (Advanced Level)
- **Strategy**: Enhance existing files + add new module for background thread
- **New Module**: `phase1/src/reminder_thread.py` for background reminder checking
- **Backward Compatibility**: Existing tasks default to `recurrence=None`, `due_date=None`, `reminder=None`
- **New Fields**:
  ```python
  task = {
      # ... existing fields ...
      "recurrence": dict | None,  # {"type": str, "interval": int, "days": list[str]}
      "due_date": datetime | None,  # When task is due
      "reminder": dict | None,  # {"offset_minutes": int, "notified": bool}
      "parent_task_id": int | None  # Links to original recurring task
  }
  ```

### Technology Stack
- **Language**: Python 3.13+ (unchanged)
- **Build Tool**: UV (unchanged)
- **Dependencies**:
  - `threading` (stdlib) - background reminder thread
  - `datetime`, `timedelta` (stdlib) - date calculations
  - `calendar` (stdlib) - month-end handling
  - `queue.Queue` (stdlib) - thread-safe notifications
- **Platform**: Cross-platform (Windows WSL 2, Linux, macOS)

## Constitution Check

### Compliance Review

**✅ Spec-First Development**
- Implementation plan follows approved spec 003-todo-advanced
- All requirements documented before code changes
- User stories prioritized (P1-P3)

**✅ AI-Native Architecture**
- All code generation performed by Claude Code
- Human provides requirements, reviews outputs

**✅ Code Quality Standards**
- Type hints required on all new methods
- Async/await: Background thread uses threading (synchronous but non-blocking)
- Error handling: Validation in CLI layer, None returns in business logic, thread-safe operations
- Zero hardcoded credentials: N/A (no external services)

**✅ Progressive Enhancement**
- Extends Intermediate Level without breaking existing functionality
- Backward compatible: existing tasks work with None defaults
- No data migration needed (in-memory storage)

**✅ Technology Constraints**
- Python 3.13+ with UV: ✅
- Manual code writing prohibited: ✅ (Claude Code generates all code)

### Deviations
None. Advanced level fully complies with constitution.

## Project Structure

### Files to Modify/Create
```
phase1/
├── src/
│   ├── task_manager.py   # ADD: recurrence/due_date/reminder methods
│   ├── main.py           # ADD: 5 new menu options (11-15), update display
│   └── reminder_thread.py # CREATE: Background thread for reminders (NEW FILE)
├── specs/
│   └── 003-todo-advanced/
│       ├── spec.md       # ✅ Created
│       ├── plan.md       # 📝 This file
│       └── tasks.md      # ⏳ Next step
└── README.md             # UPDATE: Document advanced features
```

### New File: reminder_thread.py
This is the **only new file** needed for advanced features. Creates a background thread that:
- Checks reminders every 60 seconds
- Uses thread-safe queue for notifications
- Marks reminders as notified to prevent duplicates

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   main.py (CLI Loop)                            │
│  - Display menu (16 options)                                    │
│  - Route to TaskManager methods                                 │
│  - Format output (priorities, tags, due dates, recurrence)      │
│  - Handle reminder notifications from background thread         │
│  - Check notification_queue on each menu loop                   │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│              task_manager.py (Business Logic)                   │
│  - TaskManager class                                            │
│  - Existing: CRUD + Priority + Tags + Search + Filter + Sort    │
│  - NEW: set_recurrence() - store recurrence rules               │
│  - NEW: create_next_occurrence() - clone task for recurrence    │
│  - NEW: calculate_next_due_date() - handle edge cases           │
│  - NEW: set_due_date() - with future validation                 │
│  - NEW: set_reminder() - store offset + notified flag           │
│  - NEW: get_overdue_tasks() - filter past due dates             │
│  - NEW: get_upcoming_tasks(days) - filter future range          │
│  - NEW: get_pending_reminders() - for background thread         │
│  - NEW: mark_reminder_notified() - prevent duplicates           │
│  - NEW: snooze_reminder() - reschedule for 10 minutes           │
│  - In-memory storage (tasks list) with threading.Lock           │
└──────────────┬──────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────────────────┐
│           reminder_thread.py (Background Worker)  ⚙️ NEW        │
│  - ReminderThread class extends threading.Thread               │
│  - Runs as daemon thread (stops when main app exits)            │
│  - Checks reminders every 60 seconds in while loop              │
│  - Compares current_time vs (due_date - offset_minutes)         │
│  - When reminder time reached:                                   │
│    1. Put task in notification_queue                            │
│    2. Mark reminder as notified via task_manager                │
│  - Thread-safe access using threading.Lock                      │
│  - Graceful shutdown with running flag                          │
└─────────────────────────────────────────────────────────────────┘
```

## Design Decisions

### Decision 1: Recurring Task Implementation

**Options Considered**:
1. **Clone task on completion** (chosen)
2. Single task with "next_due" field
3. Cron-style scheduler with task templates

**Trade-offs**:
- **Clone**: Creates audit trail, each occurrence is independent, clear parent-child relationship via parent_task_id
- **Single task**: Simpler data model, but loses history of completions
- **Cron scheduler**: Most flexible, but complex for Phase I in-memory storage

**Decision**: Use **clone task on completion**

**Rationale**:
- Audit trail: Can see all past occurrences in task history
- Independence: Each occurrence can be modified without affecting future ones
- Simplicity: Reuses existing task creation logic
- Parent tracking: parent_task_id links back to original for context
- Forward compatibility: When Phase II adds persistence, can query task series by parent_task_id

**Implementation**:
```python
def create_next_occurrence(self, task_id: int) -> Optional[dict]:
    """When recurring task completed, create next occurrence."""
    task = self.get_task(task_id)
    if not task or not task.get("recurrence"):
        return None

    # Calculate next due date based on recurrence type
    next_due = self.calculate_next_due_date(task)

    # Clone task with new ID, reset completion
    new_task = {
        "id": self._generate_id(),
        "title": task["title"],
        "description": task["description"],
        "completed": False,  # FRESH START
        "priority": task["priority"],
        "tags": task["tags"].copy(),
        "recurrence": task["recurrence"].copy(),
        "due_date": next_due,
        "reminder": task["reminder"].copy() if task.get("reminder") else None,
        "parent_task_id": task_id,  # LINK TO ORIGINAL
        "created_at": datetime.now().isoformat()
    }
    self.tasks.append(new_task)
    return new_task
```

---

### Decision 2: Reminder Check Frequency

**Options Considered**:
1. **Every 60 seconds** (chosen)
2. Every 10 seconds (more responsive)
3. Event-driven (sleep until next reminder)

**Trade-offs**:
- **60s**: Balanced approach, acceptable precision, low CPU usage
- **10s**: More responsive, but 6x more CPU usage for marginal benefit
- **Event-driven**: Most efficient, but complex implementation for Phase I

**Decision**: Use **60-second check interval**

**Rationale**:
- Acceptable precision: 0-59 seconds late is acceptable for user notifications
- Low overhead: Thread sleeps 60s between checks, minimal CPU usage
- Simple implementation: `time.sleep(60)` in while loop
- User expectation: "1 hour before" reminder doesn't need sub-minute precision
- Can optimize later: Phase II can add event-driven approach if needed

**Implementation**:
```python
def run(self):
    while self.running:
        self.check_reminders()
        time.sleep(60)  # Sleep for 60 seconds between checks
```

---

### Decision 3: Thread Safety Strategy

**Options Considered**:
1. **threading.Lock + Queue hybrid** (chosen)
2. Queue-based communication only (no shared data)
3. No threading (poll reminders in main loop)

**Trade-offs**:
- **Lock + Queue**: Lock protects shared task list, Queue for notifications (thread-safe by design)
- **Queue only**: Cleanest separation, but complicates task list access
- **Polling**: No thread safety issues, but blocks UI during checks

**Decision**: Use **Lock for data access + Queue for notifications**

**Rationale**:
- Separation of concerns: Lock protects tasks list mutations, Queue handles notifications
- Thread-safe by design: Queue is thread-safe without additional locking
- Simple implementation: Single lock for all task list operations
- Non-blocking UI: Background thread doesn't block main CLI loop
- Standard pattern: Widely used producer-consumer pattern in Python

**Implementation**:
```python
# In task_manager.py
class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.lock = threading.Lock()  # Protect task list access

    def get_pending_reminders(self) -> list[dict]:
        with self.lock:  # Acquire lock before accessing tasks
            return [t for t in self.tasks if ...]

# In reminder_thread.py
class ReminderThread(threading.Thread):
    def __init__(self, task_manager, notification_queue):
        super().__init__(daemon=True)
        self.task_manager = task_manager
        self.notification_queue = notification_queue  # Thread-safe Queue

    def check_reminders(self):
        now = datetime.now()
        pending = self.task_manager.get_pending_reminders()  # Uses lock internally

        for task in pending:
            if should_notify(task, now):
                self.notification_queue.put(task)  # Queue is thread-safe
                self.task_manager.mark_reminder_notified(task["id"])
```

---

### Decision 4: Due Date Storage Format

**Options Considered**:
1. **datetime object** (in-memory Python object)
2. ISO string "2026-01-03T09:00:00" (chosen)
3. Unix timestamp (numeric seconds since epoch)

**Trade-offs**:
- **datetime object**: Most convenient for calculations, but not JSON-serializable (Phase II issue)
- **ISO string**: Human-readable, JSON-serializable, timezone-aware format
- **Unix timestamp**: Compact, numeric, but less readable

**Decision**: Use **ISO string format** (internally convert to datetime for calculations)

**Rationale**:
- Forward compatibility: Phase II will persist to JSON/PostgreSQL - ISO strings work natively
- Readability: Easy to debug and inspect in task dictionaries
- Python support: `datetime.fromisoformat()` and `.isoformat()` built-in methods
- Timezone awareness: ISO format can include timezone (though Phase I uses local only)
- Calculation pattern: Parse to datetime for logic, store as ISO string

**Implementation**:
```python
def set_due_date(self, task_id: int, due_date_str: str) -> Optional[dict]:
    """Set due date from ISO string format."""
    try:
        due_date = datetime.fromisoformat(due_date_str)
    except ValueError:
        return None  # Invalid format

    if due_date < datetime.now():
        return None  # Must be future date

    task = self.get_task(task_id)
    if task:
        task["due_date"] = due_date.isoformat()  # Store as ISO string
        return task
    return None

def calculate_next_due_date(self, task: dict) -> datetime:
    """Calculate next due date (returns datetime object for internal use)."""
    current_due = datetime.fromisoformat(task["due_date"]) if task.get("due_date") else datetime.now()
    # ... calculate next_due ...
    return next_due  # Returns datetime object (caller will convert to ISO if storing)
```

---

### Decision 5: Overdue Calculation Strategy

**Options Considered**:
1. **Real-time calculation on display** (chosen)
2. Cached "is_overdue" boolean flag
3. Separate overdue_tasks list maintained by background thread

**Trade-offs**:
- **Real-time**: Always accurate, no stale data, simple logic
- **Cached flag**: Faster display, but requires update mechanism
- **Separate list**: Fast filtering, but complex maintenance

**Decision**: Use **real-time calculation** whenever task is displayed

**Rationale**:
- Always accurate: No risk of stale "overdue" flags from old calculations
- Small dataset: Phase I has manageable task count, O(n) filtering acceptable
- Simple implementation: `if task["due_date"] and datetime.now() > datetime.fromisoformat(task["due_date"])`
- No maintenance overhead: No need to update cached flags on time changes
- Can optimize later: Phase II can add indexes if performance becomes issue

**Implementation**:
```python
def get_overdue_tasks(self) -> list[dict]:
    """Get tasks that are overdue (real-time calculation)."""
    now = datetime.now()
    overdue = []

    for task in self.tasks:
        if task.get("due_date") and not task["completed"]:
            due_date = datetime.fromisoformat(task["due_date"])
            if now > due_date:
                overdue.append(task)

    return sorted(overdue, key=lambda t: t["due_date"])  # Earliest first

def format_due_date_countdown(self, task: dict) -> str:
    """Format due date as countdown or overdue message."""
    if not task.get("due_date"):
        return ""

    due_date = datetime.fromisoformat(task["due_date"])
    now = datetime.now()
    delta = due_date - now

    if delta.total_seconds() < 0:
        # Overdue
        abs_delta = abs(delta)
        if abs_delta.days > 0:
            return f"OVERDUE by {abs_delta.days} days"
        else:
            hours = int(abs_delta.seconds / 3600)
            return f"OVERDUE by {hours} hours"
    else:
        # Future
        if delta.days > 0:
            return f"due in {delta.days} days"
        else:
            hours = int(delta.seconds / 3600)
            return f"due in {hours} hours"
```

## Implementation Phases

### Phase 0: Data Model Extension (Foundation)
**Blocking**: All subsequent phases depend on this

**Changes to `task_manager.py`**:
- Modify `add_task()` to include default `recurrence=None`, `due_date=None`, `reminder=None`, `parent_task_id=None`
- Add `import threading` for Lock
- Add `self.lock = threading.Lock()` to `__init__()`
- Update task creation to include all 4 new fields

**Validation**: Create task, verify it has all 11 fields (7 existing + 4 new)

---

### Phase 1: Recurring Task Logic (User Story 1 - P1)
**Goal**: Users can create recurring tasks that auto-generate next occurrences

**Changes to `task_manager.py`**:
- Add `set_recurrence(task_id, type, interval, days)` method
  - Validate type in ["daily", "weekly", "monthly", "none"]
  - Store as dict: `{"type": type, "interval": interval, "days": days}`
- Add `calculate_next_due_date(task)` method
  - Handle daily: current + (interval × days)
  - Handle weekly: current + (interval × 7 days)
  - Handle monthly: current + (interval × months), adjust for month-end
- Add `create_next_occurrence(task_id)` method
  - Clone task with new ID
  - Reset completed to False
  - Link via parent_task_id
  - Calculate next due date
- Modify `toggle_complete(task_id)` to check for recurrence
  - If recurring task: call `create_next_occurrence()`
  - Return both completed task and new occurrence

**Changes to `main.py`**:
- Add `set_recurrence_flow(manager)` function
  - Prompt for task ID, type, interval, days (if weekly)
  - Display confirmation with recurrence indicator
- Modify `toggle_complete_flow()` to handle recurring tasks
  - Show message: "Next occurrence created: Task #X due [date]"
- Modify `delete_task_flow()` to prompt for future occurrences
  - If recurring: ask "Delete all future occurrences? (y/n)"
  - If yes: set recurrence to None before delete
- Update `view_tasks_flow()` to display recurrence indicator
  - Format: "Recurring: Daily" or "Recurring: Weekly (Mon, Wed)"

**Validation**: Create daily recurring task, mark complete, verify next occurrence created for tomorrow

---

### Phase 2: Due Date Management (User Story 2 - P2)
**Goal**: Users can set due dates and see countdowns/overdue indicators

**Changes to `task_manager.py`**:
- Add `set_due_date(task_id, due_date_str)` method
  - Parse ISO string to datetime
  - Validate future date
  - Store as ISO string
- Add `get_overdue_tasks()` method
  - Filter tasks where due_date < now and not completed
  - Return sorted by due_date (earliest first)
- Add `get_upcoming_tasks(days)` method
  - Filter tasks where now < due_date < now + days
  - Return sorted by due_date

**Changes to `main.py`**:
- Add `set_due_date_flow(manager)` function
  - Prompt for task ID and date/time (YYYY-MM-DD HH:MM)
  - Validate future date
  - Display confirmation: "Due: Jan 3, 2026 9:00 AM"
- Add `format_due_date_display(task)` helper function
  - Return human-readable: "Due: Jan 3, 2026 9:00 AM (in 2 days)"
  - Return overdue: "Due: Dec 30, 2025 5:00 PM (OVERDUE by 3 hours)"
- Add `view_overdue_flow(manager)` function
  - Call `manager.get_overdue_tasks()`
  - Display with emphasis (bold or red text)
- Add `view_upcoming_flow(manager)` function
  - Call `manager.get_upcoming_tasks(7)`
  - Display tasks due within 7 days
- Update `view_tasks_flow()` to show due dates and countdowns
- Update `filter_tasks_flow()` to add overdue/due_today/due_this_week options
- Update `sort_tasks_flow()` to add "due date (earliest first)" option

**Validation**: Set due date in future, verify countdown; set past date, verify overdue indicator

---

### Phase 3: Reminder System - Data Layer (User Story 3 - P3)
**Goal**: Store and manage reminder settings

**Changes to `task_manager.py`**:
- Add `set_reminder(task_id, offset_minutes)` method
  - Validate task has due_date (required)
  - Validate offset_minutes in [15, 60, 1440, 10080] (15min, 1hour, 1day, 1week)
  - Store as dict: `{"offset_minutes": offset_minutes, "notified": False}`
- Add `get_pending_reminders()` method
  - Return tasks with reminder not yet notified and due_date exists
  - Used by background thread
- Add `mark_reminder_notified(task_id)` method
  - Set reminder["notified"] = True
  - Thread-safe with lock
- Add `snooze_reminder(task_id, minutes)` method
  - Set notified = False
  - Adjust offset to trigger in X minutes from now

**Changes to `main.py`**:
- Add `set_reminder_flow(manager)` function
  - Prompt for task ID
  - Check if task has due_date (error if not)
  - Prompt for offset: "15min/1hour/1day/1week"
  - Map to minutes: {"15min": 15, "1hour": 60, "1day": 1440, "1week": 10080}
  - Display confirmation: "Reminder set: 1 hour before (Jan 3, 2026 8:00 AM)"

**Validation**: Set reminder on task with due date; verify stored correctly; verify error if no due date

---

### Phase 4: Background Reminder Thread (User Story 3 - P3)
**Goal**: Background thread checks and triggers reminders

**Create new file: `phase1/src/reminder_thread.py`**:
```python
import threading
import time
from datetime import datetime, timedelta
from queue import Queue

class ReminderThread(threading.Thread):
    def __init__(self, task_manager, notification_queue):
        super().__init__(daemon=True)
        self.task_manager = task_manager
        self.notification_queue = notification_queue
        self.running = True

    def run(self):
        while self.running:
            self.check_reminders()
            time.sleep(60)  # Check every 60 seconds

    def check_reminders(self):
        now = datetime.now()
        pending = self.task_manager.get_pending_reminders()

        for task in pending:
            due_date = datetime.fromisoformat(task["due_date"])
            reminder_time = due_date - timedelta(minutes=task["reminder"]["offset_minutes"])

            if now >= reminder_time:
                # Queue notification for main thread
                self.notification_queue.put(task)
                self.task_manager.mark_reminder_notified(task["id"])

    def stop(self):
        self.running = False
```

**Changes to `main.py`**:
- Import `from queue import Queue`
- Import `from reminder_thread import ReminderThread`
- Add `notification_queue = Queue()` in `main()`
- Start reminder thread: `reminder_thread = ReminderThread(manager, notification_queue)`
- In main event loop, check queue before menu:
  ```python
  while True:
      # Check for reminder notifications
      while not notification_queue.empty():
          task = notification_queue.get()
          display_reminder_notification(task, manager)

      display_menu()
      choice = get_user_choice()
      # ... existing menu routing ...
  ```
- Add `display_reminder_notification(task, manager)` function
  - Display: "⏰ REMINDER: '[task title]' is due in [time]!"
  - Prompt: "Actions: (s)nooze 10min | (v)iew task | (c)ontinue"
  - Handle snooze: call `manager.snooze_reminder(task["id"], 10)`

**Validation**: Set reminder for soon (e.g., 2 minutes from now), wait, verify notification appears in CLI

---

### Phase 5: Menu Integration & Display Updates
**Goal**: Add new menu options and update display formatting

**Changes to `main.py`**:
- Update `display_menu()` to show 16 options:
  ```
  11. Set Recurrence
  12. Set Due Date
  13. Set Reminder
  14. View Overdue Tasks
  15. View Upcoming (7 days)
  16. Exit
  ```
- Update `get_user_choice()` to validate "1-16"
- Update `main()` event loop to route choices 11-16
- Update task display format to show:
  - Recurrence indicator: "Recurring: Daily"
  - Due date with countdown: "Due: Jan 3, 2026 9:00 AM (in 2 days)"
  - Overdue emphasis: Bold or red text
  - Reminder status: "Reminder: 1 hour before" or "Reminder: Sent at 1:00 PM"

**Validation**: Menu shows all 16 options, all routing works, task display shows new fields

---

### Phase 6: Polish & Documentation
**Goal**: Final validation and README updates

**Changes to `README.md`**:
- Update feature list to include recurring tasks, due dates, reminders
- Add examples for all 3 advanced user stories
- Update data model showing all 11 fields
- Update menu showing 16 options
- Add threading note for background reminders

**Validation Tasks**:
- Test all User Story 1 acceptance scenarios (6 scenarios: daily/weekly/monthly recurrence, delete prompt, early completion)
- Test all User Story 2 acceptance scenarios (6 scenarios: due date display, countdown, overdue, filter, sort)
- Test all User Story 3 acceptance scenarios (6 scenarios: reminder setup, notification, snooze, status display)
- Test all edge cases (8 edge cases: month-end handling, early completion, multiple reminders, etc.)
- Verify full demo workflow completes in <90 seconds

## Testing Strategy

### Manual Validation (Phase I approach)
No automated tests - manual validation against acceptance scenarios.

**Test Cases to Verify**:

**Recurring Tasks (US1)**:
1. Create daily recurring task → mark complete → verify next created for tomorrow
2. Create weekly recurring task (Mon, Wed) → mark complete Monday → verify next is Wednesday (2 days later)
3. Create monthly recurring task on Jan 31 → mark complete → verify next is Feb 28/29 (last day of month)
4. Delete recurring task → verify prompt "Delete all future occurrences?"
5. Complete recurring task 2 days early → verify next still based on original schedule
6. View recurring task → verify "Recurring: Weekly (Mon, Wed)" indicator displayed

**Due Dates (US2)**:
1. Set due date in future → verify displays "Due: Jan 3, 2026 9:00 AM (in 2 days)"
2. Set due date in past → verify error "Due date must be in the future"
3. Let task become overdue → verify displays "OVERDUE by 3 hours" with emphasis
4. Filter by overdue → verify only overdue tasks shown
5. Sort by due date → verify earliest due date first
6. View upcoming (7 days) → verify only tasks within 7 days shown

**Reminders (US3)**:
1. Set reminder without due date → verify error "Cannot set reminder on task without due date"
2. Set reminder "1hour" before due → verify stored as 60 minutes offset
3. Wait for reminder time → verify notification "⏰ REMINDER: [task] is due in 1 hour!"
4. Acknowledge reminder → verify marked as notified=true (no duplicate notifications)
5. Snooze reminder → verify notification appears again in 10 minutes
6. View task with reminder → verify shows "Reminder: 1 hour before" or "Reminder: Sent at 1:00 PM"

**Edge Cases**:
1. Monthly recurrence on day 31, next month has 30 days → uses day 30
2. Complete recurring task early → next based on original schedule
3. Multiple reminders at same time → all display in sequence
4. Reminder for overdue task → no notification (past due)
5. Set due date to current minute → immediately becomes overdue
6. Background thread CPU usage → minimal (sleeps 60s between checks)

### Acceptance Criteria Validation
- [ ] User Story 1: All 6 acceptance scenarios pass
- [ ] User Story 2: All 6 acceptance scenarios pass
- [ ] User Story 3: All 6 acceptance scenarios pass
- [ ] All 8 edge cases handled correctly

## Dependencies

### Requires
- **Spec 002-todo-intermediate**: Intermediate implementation must be complete ✅
- **Files**: `phase1/src/task_manager.py`, `phase1/src/main.py` must exist ✅
- **Python stdlib**: `threading`, `datetime`, `timedelta`, `calendar`, `queue.Queue`

### Blocks
None - this is the final Phase I enhancement

### Related
- **Phase II**: Will add persistence for recurring tasks, due dates, and reminders to database
- **Phase III**: AI chatbot will interact with advanced task features

## Risks and Mitigations

### Risk 1: Thread Safety Issues
**Probability**: Medium
**Impact**: High (data corruption, race conditions)
**Mitigation**:
- Use `threading.Lock()` for all task list access
- Use `Queue()` for thread-safe notifications (no manual locking needed)
- Test with concurrent operations (add task while reminder thread checks)
- Use `daemon=True` so thread exits cleanly with main app

### Risk 2: Month-End Date Calculations
**Probability**: Low
**Impact**: Medium (incorrect next occurrence dates)
**Mitigation**:
- Use `calendar.monthrange(year, month)[1]` to get last day of month
- Test edge cases: Jan 31 → Feb 28/29, May 31 → Jun 30, Dec 31 → Jan 31
- Formula: `day = min(current_day, last_day_of_target_month)`

### Risk 3: Background Thread Not Stopping
**Probability**: Low
**Impact**: Low (thread continues after app exits)
**Mitigation**:
- Use `daemon=True` when creating thread (automatically stops with main process)
- Implement `stop()` method with `self.running = False` for graceful shutdown
- No explicit cleanup needed in Phase I (daemon handles it)

### Risk 4: Reminder Notification Blocking CLI
**Probability**: Medium
**Impact**: Medium (poor user experience)
**Mitigation**:
- Check notification queue **before** displaying menu (non-blocking)
- Use `Queue.get_nowait()` or `Queue.empty()` check to avoid blocking
- Keep notification display simple (single line + prompt)
- Allow "continue" option to dismiss quickly

## Success Criteria

### Implementation Complete When
- [ ] All 3 user stories (US1-US3) implemented and tested
- [ ] All 28 new functional requirements (FR-031 to FR-058) met
- [ ] All 11 new success criteria (SC-023 to SC-033) verified
- [ ] All edge cases from spec handled correctly
- [ ] README.md updated with advanced features
- [ ] Full demo workflow (recurring task with due date + reminder) completes in <90 seconds
- [ ] Background reminder thread runs without blocking CLI
- [ ] Thread-safe operations (no race conditions with concurrent access)

### Code Quality Checklist
- [ ] Type hints on all new methods
- [ ] Docstrings on all new functions
- [ ] Thread-safe operations with proper locking
- [ ] Input validation in CLI layer
- [ ] Error handling for invalid inputs
- [ ] Date validation (future dates only)
- [ ] Edge case handling (month-end, early completion)
- [ ] PEP 8 compliant

## Next Steps

1. **Create tasks.md**: Break down this plan into specific tasks (T173-T250+)
2. **Run `/sp.implement`**: Execute all tasks sequentially
3. **Manual validation**: Test against all acceptance scenarios
4. **Update README.md**: Document all 10 features (5 Basic + 3 Intermediate + 2 Advanced)
5. **Create demo**: Show full advanced workflow in <90 seconds
6. **Commit**: `feat: add recurring tasks, due dates, and reminders to Phase I app`

---

**Plan Version**: 1.0
**Estimated Complexity**: High (new background thread, date calculations, thread safety)
**Estimated Tasks**: ~80 tasks across 6 phases
**Estimated Time**: ~6 hours (single developer, sequential implementation)
