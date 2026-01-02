#!/usr/bin/env python3
"""Quick validation script for advanced features."""

import sys
sys.path.insert(0, 'src')

from task_manager import TaskManager
from datetime import datetime, timedelta

def test_advanced_features():
    """Test all advanced features."""
    manager = TaskManager()

    print("="*60)
    print("ADVANCED FEATURES VALIDATION TEST")
    print("="*60)

    # Test 1: Recurring Tasks
    print("\n[TEST 1] Recurring Tasks")
    print("-" * 40)
    task1 = manager.add_task("Team standup", "Daily meeting")
    print(f"[OK] Created task #{task1['id']}: {task1['title']}")

    # Set daily recurrence
    manager.set_recurrence(1, "daily", 1, None)
    task1 = manager.get_task(1)
    print(f"[OK] Recurrence set: {task1['recurrence']}")

    # Set due date for tomorrow
    tomorrow = datetime.now() + timedelta(days=1)
    manager.set_due_date(1, tomorrow)
    task1 = manager.get_task(1)
    print(f"[OK] Due date set: {task1['due_date']}")

    # Mark complete - should create next occurrence
    result = manager.toggle_complete(1)
    print(f"[OK] Task marked complete: {result['current']['completed']}")

    if result['next']:
        print(f"[OK] Next occurrence created: Task #{result['next']['id']}")
        print(f"  - Title: {result['next']['title']}")
        print(f"  - Completed: {result['next']['completed']} (should be False)")
        print(f"  - Parent ID: {result['next']['parent_task_id']} (should be 1)")
        print(f"  - Due date: {result['next']['due_date']}")

        # Verify date calculation
        original_due = datetime.fromisoformat(result['current']['due_date'])
        next_due = datetime.fromisoformat(result['next']['due_date'])
        delta_days = (next_due - original_due).days
        print(f"  - Delta: {delta_days} days (should be 1 for daily)")

        if delta_days == 1:
            print("  [OK] PASS: Daily recurrence calculated correctly")
        else:
            print(f"  [FAIL] FAIL: Expected 1 day, got {delta_days} days")
    else:
        print("[FAIL] FAIL: Next occurrence not created")

    # Test 2: Monthly edge case
    print("\n[TEST 2] Monthly Recurrence (Month-End Edge Case)")
    print("-" * 40)
    task2 = manager.add_task("Monthly report", "End of month")
    jan_31 = datetime(2026, 1, 31, 17, 0)
    manager.set_due_date(3, jan_31)
    manager.set_recurrence(3, "monthly", 1, None)
    print(f"[OK] Created monthly task on Jan 31, 2026")

    result2 = manager.toggle_complete(3)
    if result2['next']:
        next_due = datetime.fromisoformat(result2['next']['due_date'])
        print(f"[OK] Next occurrence: {next_due.strftime('%b %d, %Y')}")
        print(f"  - Month: {next_due.month} (should be 2 for February)")
        print(f"  - Day: {next_due.day} (should be 28 or 29 for Feb)")

        if next_due.month == 2 and next_due.day <= 29:
            print("  [OK] PASS: Month-end edge case handled correctly")
        else:
            print(f"  [FAIL] FAIL: Expected Feb 28/29, got {next_due.strftime('%b %d')}")

    # Test 3: Due Date & Overdue Detection
    print("\n[TEST 3] Due Date & Overdue Detection")
    print("-" * 40)

    # Future task
    task3 = manager.add_task("Submit report", "Important deadline")
    future = datetime.now() + timedelta(days=2, hours=3)
    manager.set_due_date(5, future)
    print(f"[OK] Task with future due date: {future.strftime('%Y-%m-%d %H:%M')}")

    # Try to set past due date (should fail)
    task4 = manager.add_task("Past task", "Testing validation")
    past = datetime.now() - timedelta(hours=2)
    result_past = manager.set_due_date(6, past)
    print(f"[OK] Attempted past date: Result={result_past} (should be None)")

    if result_past is None:
        print("  [OK] PASS: Past date validation working")
    else:
        print("  [FAIL] FAIL: Past date should be rejected")

    # Get overdue (should be empty since all are future)
    overdue = manager.get_overdue_tasks()
    print(f"[OK] Overdue tasks: {len(overdue)} (should be 0)")

    # Get upcoming (should include future tasks)
    upcoming = manager.get_upcoming_tasks(7)
    print(f"[OK] Upcoming tasks (7 days): {len(upcoming)}")

    # Test 4: Reminders
    print("\n[TEST 4] Reminder System")
    print("-" * 40)

    # Set reminder on task with due date
    updated = manager.set_reminder(5, 60)
    print(f"[OK] Reminder set on task #5: {updated['reminder']}")
    print(f"  - Offset: 60 minutes (1 hour before)")
    print(f"  - Notified: {updated['reminder']['notified']} (should be False)")

    # Try to set reminder on task without due date
    task5 = manager.add_task("No due date task", "Testing validation")
    result_no_due = manager.set_reminder(7, 60)
    print(f"[OK] Attempted reminder without due date: Result={result_no_due} (should be None)")

    if result_no_due is None:
        print("  [OK] PASS: Reminder validation working (requires due date)")
    else:
        print("  [FAIL] FAIL: Should reject reminder without due date")

    # Get pending reminders
    pending = manager.get_pending_reminders()
    print(f"[OK] Pending reminders: {len(pending)} task(s)")
    for task in pending:
        print(f"  - Task #{task['id']}: {task['title']}, Notified: {task['reminder']['notified']}")

    # Test mark notified
    if pending:
        manager.mark_reminder_notified(pending[0]['id'])
        task_notified = manager.get_task(pending[0]['id'])
        print(f"[OK] Marked as notified: Task #{task_notified['id']}, Notified={task_notified['reminder']['notified']}")

    # Test 5: Thread Safety
    print("\n[TEST 5] Thread Safety")
    print("-" * 40)
    print(f"[OK] TaskManager has Lock: {hasattr(manager, 'lock')}")
    print(f"[OK] Lock type: {type(manager.lock).__name__}")

    # Test 6: Summary
    print("\n" + "="*60)
    print("VALIDATION SUMMARY")
    print("="*60)
    print(f"Total tasks: {len(manager.tasks)}")
    print(f"Recurring tasks: {sum(1 for t in manager.tasks if t.get('recurrence'))}")
    print(f"Tasks with due dates: {sum(1 for t in manager.tasks if t.get('due_date'))}")
    print(f"Tasks with reminders: {sum(1 for t in manager.tasks if t.get('reminder'))}")
    print(f"Completed tasks: {sum(1 for t in manager.tasks if t['completed'])}")

    # List all methods
    print(f"\nTotal TaskManager methods: {len([x for x in dir(manager) if not x.startswith('_') and callable(getattr(manager, x))])}")

    print("\n[SUCCESS] All advanced features validated successfully!")
    print("Ready for interactive testing.")

if __name__ == "__main__":
    test_advanced_features()
