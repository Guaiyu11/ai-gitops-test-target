"""Delete task command."""

import json
from pathlib import Path


def get_tasks_file():
    """Get path to tasks file."""
    return Path.home() / ".local" / "share" / "task-cli" / "tasks.json"


def validate_task_id(tasks, task_id):
    """Validate task ID exists."""
    if task_id < 1 or task_id > len(tasks):
        raise ValueError(f"Invalid task ID: {task_id}")
    return task_id


def delete_task(task_id):
    """Delete a task by ID."""
    tasks_file = get_tasks_file()
    if not tasks_file.exists():
        print("No tasks found!")
        return

    tasks = json.loads(tasks_file.read_text())
    if not tasks:
        print("No tasks found!")
        return

    validate_task_id(tasks, task_id)

    deleted_desc = None
    for task in tasks:
        if task["id"] == task_id:
            deleted_desc = task["description"]
            break

    tasks = [t for t in tasks if t["id"] != task_id]
    # Re-number IDs to avoid gaps
    for i, task in enumerate(tasks, 1):
        task["id"] = i

    tasks_file.write_text(json.dumps(tasks, indent=2))
    print(f"Deleted task {task_id}: {deleted_desc}")