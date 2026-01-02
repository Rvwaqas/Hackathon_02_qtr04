"""
Main CLI Module - User Interface

This module provides the command-line interface for the todo application.
Handles user input, menu display, and interaction flows.
"""

from datetime import datetime, timedelta
from queue import Queue
from task_manager import TaskManager
from reminder_thread import ReminderThread


def display_menu() -> None:
    """Display numbered menu options."""
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
    print("11. Set Recurrence")
    print("12. Set Due Date")
    print("13. Set Reminder")
    print("14. View Overdue Tasks")
    print("15. View Upcoming (7 days)")
    print("16. Exit")


def get_user_choice() -> str:
    """
    Prompt for menu choice and validate.

    Returns:
        str: Valid menu choice (1-16)
    """
    while True:
        choice = input("\nEnter choice: ").strip()
        if choice in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]:
            return choice
        print("Invalid choice. Please enter 1-16.")


def add_task_flow(manager: TaskManager) -> None:
    """
    Prompt for task details and create task.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Add Task ---")

    # Get title
    while True:
        title = input("Title (required, 1-200 chars): ").strip()
        if not title:
            print("Error: Title is required (1-200 characters)")
            continue
        if len(title) > 200:
            print("Error: Title max 200 characters")
            continue
        break

    # Get description
    while True:
        description = input("Description (optional, max 1000 chars): ").strip()
        if len(description) > 1000:
            print("Error: Description max 1000 characters")
            continue
        break

    # Create task
    task = manager.add_task(title, description)
    print(f"\n[OK] Task #{task['id']} created: {task['title']}")


def view_tasks_flow(manager: TaskManager) -> None:
    """
    Display all tasks with formatting.

    Args:
        manager: TaskManager instance
    """
    print("\n--- All Tasks ---")

    tasks = manager.get_all_tasks()

    if not tasks:
        print("No tasks yet! Create your first task to get started.")
        return

    for task in tasks:
        # Priority indicator
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        priority_display = f"{priority_str} " if priority_str else ""

        # Visual indicator for completion
        indicator = "[X]" if task["completed"] else "[ ]"

        # Status
        status = "Completed" if task["completed"] else "Pending"

        # Tags display
        tags_display = ""
        if task.get("tags"):
            tags_display = " " + " ".join(f"#{tag}" for tag in task["tags"])

        # Description preview (50 chars)
        desc_preview = task["description"][:50]
        if len(task["description"]) > 50:
            desc_preview += "..."

        # Display with priority and tags
        print(f"{priority_display}{indicator} {task['id']}. {task['title']} ({status}){tags_display}")
        if task["description"]:
            print(f"   {desc_preview}")


def toggle_complete_flow(manager: TaskManager) -> None:
    """
    Toggle task completion status.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Mark Complete/Incomplete ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    result = manager.toggle_complete(task_id)

    if not result["current"]:
        print(f"Error: Task ID {task_id} not found")
        return

    task = result["current"]
    status = "completed" if task["completed"] else "incomplete"
    print(f"\n[OK] Task #{task_id} marked as {status}: {task['title']}")

    # Check if next occurrence was created for recurring task
    if result["next"]:
        next_task = result["next"]
        if next_task.get("due_date"):
            due_str = datetime.fromisoformat(next_task["due_date"]).strftime("%b %d, %Y")
            print(f"[OK] Next occurrence created: Task #{next_task['id']} due {due_str}")
        else:
            print(f"[OK] Next occurrence created: Task #{next_task['id']}")


def update_task_flow(manager: TaskManager) -> None:
    """
    Update task title or description.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Update Task ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    print(f"\nCurrent task: {task['title']}")
    print(f"Description: {task['description']}")

    # Get new title
    print("\nEnter new title (press Enter to keep current):")
    new_title = input().strip()

    # Validate title if provided
    if new_title:
        if len(new_title) > 200:
            print("Error: Title max 200 characters")
            return
    else:
        new_title = None

    # Get new description
    print("Enter new description (press Enter to keep current):")
    new_description = input().strip()

    # Validate description if provided
    if new_description and len(new_description) > 1000:
        print("Error: Description max 1000 characters")
        return

    if not new_description:
        new_description = None

    # Show before/after
    if new_title or new_description:
        print(f"\nBefore: {task['title']}")
        updated_task = manager.update_task(task_id, new_title, new_description)
        print(f"After: {updated_task['title']}")
        print("[OK] Task updated successfully")
    else:
        print("No changes made")


def delete_task_flow(manager: TaskManager) -> None:
    """
    Delete task with confirmation.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Delete Task ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    # Confirm
    confirm = input(f"Are you sure you want to delete task ID {task_id}? (y/n): ").strip().lower()

    if confirm == "y":
        title = task["title"]
        if manager.delete_task(task_id):
            print(f"\n[OK] Task deleted: {title}")
    else:
        print("Delete cancelled")


def set_priority_flow(manager: TaskManager) -> None:
    """
    Set task priority level.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Set Priority ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    print(f"\nCurrent task: {task['title']}")
    print(f"Current priority: {task.get('priority', 'none')}")
    print("\nPriority options:")
    print("1. high")
    print("2. medium")
    print("3. low")
    print("4. none")

    priority = input("\nEnter priority (high/medium/low/none): ").strip().lower()

    updated_task = manager.set_priority(task_id, priority)
    if not updated_task:
        print("Error: Invalid priority. Use: high, medium, low, none")
        return

    priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
    indicator = priority_indicators.get(priority, "")
    print(f"\n[OK] Priority set to {priority} {indicator}: {updated_task['title']}")


def manage_tags_flow(manager: TaskManager) -> None:
    """
    Add or remove tags from a task.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Manage Tags ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    print(f"\nCurrent task: {task['title']}")
    current_tags = task.get("tags", [])
    if current_tags:
        print(f"Current tags: {' '.join('#' + tag for tag in current_tags)}")
    else:
        print("Current tags: (none)")

    print("\n1. Add tags")
    print("2. Remove tags")
    choice = input("\nChoice: ").strip()

    if choice == "1":
        tags_input = input("Enter tags (comma-separated, max 5 total): ").strip()
        if not tags_input:
            print("No tags entered")
            return

        new_tags = [tag.strip() for tag in tags_input.split(",")]
        updated_task = manager.add_tags(task_id, new_tags)

        if not updated_task:
            print("Error: Invalid tags or max 5 tags exceeded")
            print("Tags must be alphanumeric, 1-20 characters each")
            return

        print(f"\n[OK] Tags updated: {' '.join('#' + tag for tag in updated_task['tags'])}")

    elif choice == "2":
        if not current_tags:
            print("No tags to remove")
            return

        tags_input = input("Enter tags to remove (comma-separated): ").strip()
        if not tags_input:
            print("No tags entered")
            return

        tags_to_remove = [tag.strip() for tag in tags_input.split(",")]
        updated_task = manager.remove_tags(task_id, tags_to_remove)

        if updated_task:
            if updated_task["tags"]:
                print(f"\n[OK] Tags updated: {' '.join('#' + tag for tag in updated_task['tags'])}")
            else:
                print("\n[OK] All tags removed")
    else:
        print("Invalid choice")


def search_tasks_flow(manager: TaskManager) -> None:
    """
    Search tasks by keyword.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Search Tasks ---")

    keyword = input("Enter search keyword: ").strip()

    results = manager.search_tasks(keyword)

    if not results:
        print(f"\nNo tasks found matching '{keyword}'")
        return

    print(f"\nFound {len(results)} tasks matching '{keyword}':")
    print()

    for task in results:
        # Priority indicator
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        priority_display = f"{priority_str} " if priority_str else ""

        # Visual indicator
        indicator = "[X]" if task["completed"] else "[ ]"

        # Tags display
        tags_display = ""
        if task.get("tags"):
            tags_display = " " + " ".join(f"#{tag}" for tag in task["tags"])

        # Display
        print(f"{priority_display}{indicator} {task['id']}. {task['title']}{tags_display}")
        if task["description"]:
            desc_preview = task["description"][:50]
            if len(task["description"]) > 50:
                desc_preview += "..."
            print(f"   {desc_preview}")


def filter_tasks_flow(manager: TaskManager) -> None:
    """
    Filter tasks by status, priority, or tag.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Filter Tasks ---")
    print("1. Filter by Status")
    print("2. Filter by Priority")
    print("3. Filter by Tag")
    print("4. Combined Filter")

    choice = input("\nChoice: ").strip()

    status = None
    priority = None
    tag = None

    if choice == "1":
        print("\nStatus options: all, pending, completed")
        status = input("Enter status: ").strip().lower()
    elif choice == "2":
        print("\nPriority options: high, medium, low, none")
        priority = input("Enter priority: ").strip().lower()
    elif choice == "3":
        tag = input("Enter tag name: ").strip()
    elif choice == "4":
        print("\nCombined Filter (press Enter to skip any filter)")
        status_input = input("Status (all/pending/completed): ").strip().lower()
        if status_input:
            status = status_input
        priority_input = input("Priority (high/medium/low/none): ").strip().lower()
        if priority_input:
            priority = priority_input
        tag_input = input("Tag: ").strip()
        if tag_input:
            tag = tag_input
    else:
        print("Invalid choice")
        return

    results = manager.filter_tasks(status=status, priority=priority, tag=tag)
    total_tasks = len(manager.tasks)

    if not results:
        print("\nNo tasks found matching filters")
        return

    print(f"\nShowing {len(results)} of {total_tasks} tasks:")
    print()

    for task in results:
        # Priority indicator
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        priority_display = f"{priority_str} " if priority_str else ""

        # Visual indicator
        indicator = "[X]" if task["completed"] else "[ ]"

        # Tags display
        tags_display = ""
        if task.get("tags"):
            tags_display = " " + " ".join(f"#{tag}" for tag in task["tags"])

        # Display
        print(f"{priority_display}{indicator} {task['id']}. {task['title']}{tags_display}")
        if task["description"]:
            desc_preview = task["description"][:50]
            if len(task["description"]) > 50:
                desc_preview += "..."
            print(f"   {desc_preview}")


def sort_tasks_flow(manager: TaskManager) -> None:
    """
    Sort tasks by various criteria.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Sort Tasks ---")
    print("1. Created (newest first)")
    print("2. Created (oldest first)")
    print("3. Title (A-Z)")
    print("4. Title (Z-A)")
    print("5. Priority (high -> low)")
    print("6. Priority (low -> high)")
    print("7. Status")

    choice = input("\nChoice: ").strip()

    sort_criteria_map = {
        "1": ("created", True),
        "2": ("created", False),
        "3": ("title", False),
        "4": ("title", True),
        "5": ("priority", False),  # Will be reversed in sort_tasks()
        "6": ("priority", True),   # Will be reversed in sort_tasks()
        "7": ("status", False)
    }

    if choice not in sort_criteria_map:
        print("Invalid choice")
        return

    sort_by, reverse = sort_criteria_map[choice]
    results = manager.sort_tasks(sort_by, reverse)

    sort_labels = {
        "1": "Created (newest first)",
        "2": "Created (oldest first)",
        "3": "Title (A-Z)",
        "4": "Title (Z-A)",
        "5": "Priority (high -> low)",
        "6": "Priority (low -> high)",
        "7": "Status"
    }

    print(f"\nSorted by: {sort_labels[choice]}")
    print()

    if not results:
        print("No tasks yet!")
        return

    for task in results:
        # Priority indicator
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        priority_display = f"{priority_str} " if priority_str else ""

        # Visual indicator
        indicator = "[X]" if task["completed"] else "[ ]"

        # Tags display
        tags_display = ""
        if task.get("tags"):
            tags_display = " " + " ".join(f"#{tag}" for tag in task["tags"])

        # Display
        print(f"{priority_display}{indicator} {task['id']}. {task['title']}{tags_display}")
        if task["description"]:
            desc_preview = task["description"][:50]
            if len(task["description"]) > 50:
                desc_preview += "..."
            print(f"   {desc_preview}")


def set_recurrence_flow(manager: TaskManager) -> None:
    """
    Set task recurrence pattern.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Set Recurrence ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    print(f"\nCurrent task: {task['title']}")
    print("\nRecurrence Type:")
    print("1. Daily")
    print("2. Weekly")
    print("3. Monthly")
    print("4. None (remove recurrence)")

    choice = input("\nChoice: ").strip()

    rec_types = {"1": "daily", "2": "weekly", "3": "monthly", "4": "none"}
    rec_type = rec_types.get(choice)

    if not rec_type:
        print("Invalid choice")
        return

    interval = 1
    days = None

    if rec_type == "weekly":
        days_input = input("Days (comma-separated, e.g., mon,wed,fri): ").strip()
        if days_input:
            days = [d.strip().lower() for d in days_input.split(",")]

    updated_task = manager.set_recurrence(task_id, rec_type, interval, days)

    if not updated_task:
        print("Error: Invalid recurrence type")
        return

    if rec_type == "none":
        print("\n[OK] Recurrence removed")
    else:
        rec_display = f"Recurring: {rec_type.capitalize()}"
        if days:
            days_str = ", ".join(d.capitalize()[:3] for d in days)
            rec_display += f" ({days_str})"
        print(f"\n[OK] {rec_display}")


def set_due_date_flow(manager: TaskManager) -> None:
    """
    Set task due date.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Set Due Date ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    print(f"\nCurrent task: {task['title']}")

    date_str = input("Due date (YYYY-MM-DD HH:MM): ").strip()

    try:
        due_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M")
    except ValueError:
        print("Error: Invalid date format. Use: YYYY-MM-DD HH:MM")
        return

    updated_task = manager.set_due_date(task_id, due_date)

    if not updated_task:
        print("Error: Due date must be in the future")
        return

    print(f"\n[OK] Due date set: {due_date.strftime('%b %d, %Y %I:%M %p')}")


def set_reminder_flow(manager: TaskManager) -> None:
    """
    Set reminder for task.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Set Reminder ---")

    try:
        task_id = int(input("Task ID: ").strip())
    except ValueError:
        print("Error: Please enter a valid task ID number")
        return

    task = manager.get_task(task_id)
    if not task:
        print(f"Error: Task ID {task_id} not found")
        return

    if not task.get("due_date"):
        print("Error: Task must have a due date before setting reminder")
        return

    print(f"\nCurrent task: {task['title']}")
    print(f"Due: {datetime.fromisoformat(task['due_date']).strftime('%b %d, %Y %I:%M %p')}")

    print("\nReminder Options:")
    print("1. 15 minutes before")
    print("2. 1 hour before")
    print("3. 1 day before")
    print("4. 1 week before")

    choice = input("\nChoice: ").strip()

    offset_map = {"1": 15, "2": 60, "3": 1440, "4": 10080}
    offset_minutes = offset_map.get(choice)

    if not offset_minutes:
        print("Invalid choice")
        return

    updated_task = manager.set_reminder(task_id, offset_minutes)

    if not updated_task:
        print("Error: Could not set reminder")
        return

    # Calculate reminder trigger time
    due_date = datetime.fromisoformat(task["due_date"])
    reminder_time = due_date - timedelta(minutes=offset_minutes)

    offset_labels = {"1": "15 minutes", "2": "1 hour", "3": "1 day", "4": "1 week"}
    print(f"\n[OK] Reminder set: {offset_labels[choice]} before")
    print(f"Reminder will trigger at: {reminder_time.strftime('%b %d, %Y %I:%M %p')}")


def view_overdue_flow(manager: TaskManager) -> None:
    """
    View overdue tasks.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Overdue Tasks ---")

    overdue = manager.get_overdue_tasks()

    if not overdue:
        print("No overdue tasks!")
        return

    print(f"\n\033[91mOverdue Tasks: {len(overdue)}\033[0m\n")

    for task in overdue:
        # Priority indicator
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        priority_display = f"{priority_str} " if priority_str else ""

        # Visual indicator
        indicator = "[X]" if task["completed"] else "[ ]"

        # Tags display
        tags_display = ""
        if task.get("tags"):
            tags_display = " " + " ".join(f"#{tag}" for tag in task["tags"])

        # Calculate overdue duration
        due_date = datetime.fromisoformat(task["due_date"])
        overdue_delta = datetime.now() - due_date

        if overdue_delta.days > 0:
            overdue_str = f"OVERDUE by {overdue_delta.days} days"
        else:
            hours = int(overdue_delta.seconds / 3600)
            overdue_str = f"OVERDUE by {hours} hours"

        # Display in red
        print(f"\033[91m{priority_display}{indicator} {task['id']}. {task['title']}{tags_display}\033[0m")
        print(f"\033[91m   Due: {due_date.strftime('%b %d, %Y %I:%M %p')} ({overdue_str})\033[0m")
        if task["description"]:
            desc_preview = task["description"][:50]
            if len(task["description"]) > 50:
                desc_preview += "..."
            print(f"   {desc_preview}")
        print()


def view_upcoming_flow(manager: TaskManager) -> None:
    """
    View tasks due in next 7 days.

    Args:
        manager: TaskManager instance
    """
    print("\n--- Upcoming Tasks (Next 7 Days) ---")

    upcoming = manager.get_upcoming_tasks(7)

    if not upcoming:
        print("No tasks due in the next 7 days!")
        return

    print(f"\nUpcoming Tasks: {len(upcoming)}\n")

    for task in upcoming:
        # Priority indicator
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        priority_display = f"{priority_str} " if priority_str else ""

        # Visual indicator
        indicator = "[X]" if task["completed"] else "[ ]"

        # Tags display
        tags_display = ""
        if task.get("tags"):
            tags_display = " " + " ".join(f"#{tag}" for tag in task["tags"])

        # Calculate countdown
        due_date = datetime.fromisoformat(task["due_date"])
        countdown_delta = due_date - datetime.now()

        if countdown_delta.days > 0:
            countdown_str = f"in {countdown_delta.days} days"
        else:
            hours = int(countdown_delta.seconds / 3600)
            countdown_str = f"in {hours} hours"

        # Display
        print(f"{priority_display}{indicator} {task['id']}. {task['title']}{tags_display}")
        print(f"   Due: {due_date.strftime('%b %d, %Y %I:%M %p')} ({countdown_str})")
        if task["description"]:
            desc_preview = task["description"][:50]
            if len(task["description"]) > 50:
                desc_preview += "..."
            print(f"   {desc_preview}")
        print()


def display_reminder_notification(task: dict, manager: TaskManager) -> None:
    """
    Display reminder notification with action options.

    Args:
        task: Task dictionary with reminder
        manager: TaskManager instance for snooze operations
    """
    print("\n" + "=" * 60)
    print(f"⏰ REMINDER: \"{task['title']}\" is due soon!")

    # Calculate time until due
    due_date = datetime.fromisoformat(task["due_date"])
    time_until_due = due_date - datetime.now()

    if time_until_due.days > 0:
        print(f"Due in: {time_until_due.days} days")
    else:
        hours = int(time_until_due.seconds / 3600)
        minutes = int((time_until_due.seconds % 3600) / 60)
        print(f"Due in: {hours} hours {minutes} minutes")

    print("=" * 60)

    action = input("Actions: (s)nooze 10min | (v)iew task | (c)ontinue: ").strip().lower()

    if action == "s":
        manager.snooze_reminder(task["id"], 10)
        print("[OK] Reminder snoozed for 10 minutes")
    elif action == "v":
        # Display full task details
        priority_indicators = {"high": "[H]", "medium": "[M]", "low": "[L]", "none": ""}
        priority_str = priority_indicators.get(task.get("priority", "none"), "")
        indicator = "[X]" if task["completed"] else "[ ]"
        tags = " ".join(f"#{tag}" for tag in task.get("tags", []))

        print(f"\n{priority_str} {indicator} {task['id']}. {task['title']} {tags}")
        if task["description"]:
            print(f"Description: {task['description']}")
        print(f"Due: {due_date.strftime('%b %d, %Y %I:%M %p')}")
        if task.get("recurrence"):
            print(f"Recurring: {task['recurrence']['type'].capitalize()}")
    # Continue option - just returns to menu


def main() -> None:
    """Main event loop with background reminder thread."""
    manager = TaskManager()

    # Create notification queue for thread-safe communication
    notification_queue = Queue()

    # Start background reminder thread
    reminder_thread = ReminderThread(manager, notification_queue)
    reminder_thread.start()

    print("Welcome to Console Todo App!")
    print("Phase I - In-memory storage demo (with reminders)")

    while True:
        # Check for pending reminder notifications
        while not notification_queue.empty():
            task = notification_queue.get()
            display_reminder_notification(task, manager)

        display_menu()
        choice = get_user_choice()

        if choice == "1":
            add_task_flow(manager)
        elif choice == "2":
            view_tasks_flow(manager)
        elif choice == "3":
            update_task_flow(manager)
        elif choice == "4":
            delete_task_flow(manager)
        elif choice == "5":
            toggle_complete_flow(manager)
        elif choice == "6":
            set_priority_flow(manager)
        elif choice == "7":
            manage_tags_flow(manager)
        elif choice == "8":
            search_tasks_flow(manager)
        elif choice == "9":
            filter_tasks_flow(manager)
        elif choice == "10":
            sort_tasks_flow(manager)
        elif choice == "11":
            set_recurrence_flow(manager)
        elif choice == "12":
            set_due_date_flow(manager)
        elif choice == "13":
            set_reminder_flow(manager)
        elif choice == "14":
            view_overdue_flow(manager)
        elif choice == "15":
            view_upcoming_flow(manager)
        elif choice == "16":
            print("\nGoodbye! (Note: All tasks will be lost as they're stored in memory only)")
            reminder_thread.stop()
            break


if __name__ == "__main__":
    main()
