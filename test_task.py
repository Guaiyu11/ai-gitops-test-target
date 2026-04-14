"""Basic tests for task CLI."""

import json
import pytest
from pathlib import Path
from commands.add import add_task, validate_description
from commands.done import validate_task_id
from commands.delete import delete_task, validate_task_id as validate_task_id_delete


def test_validate_description():
    """Test description validation."""
    assert validate_description("  test  ") == "test"

    with pytest.raises(ValueError):
        validate_description("")

    with pytest.raises(ValueError):
        validate_description("x" * 201)


def test_validate_task_id():
    """Test task ID validation."""
    tasks = [{"id": 1}, {"id": 2}]
    assert validate_task_id(tasks, 1) == 1

    with pytest.raises(ValueError):
        validate_task_id(tasks, 0)

    with pytest.raises(ValueError):
        validate_task_id(tasks, 99)


def test_validate_task_id_delete():
    """Test task ID validation for delete command."""
    tasks = [{"id": 1}, {"id": 2}, {"id": 3}]
    assert validate_task_id_delete(tasks, 1) == 1
    assert validate_task_id_delete(tasks, 2) == 2
    assert validate_task_id_delete(tasks, 3) == 3

    with pytest.raises(ValueError):
        validate_task_id_delete(tasks, 0)

    with pytest.raises(ValueError):
        validate_task_id_delete(tasks, 99)


def test_delete_task(tmp_path, monkeypatch):
    """Test deleting a task re-numbers remaining tasks."""
    # Monkeypatch get_tasks_file to use temp directory
    from commands import delete as delete_module
    monkeypatch.setattr(delete_module, "get_tasks_file", lambda: tmp_path / "tasks.json")

    # Create a task file with 3 tasks
    tasks_file = tmp_path / "tasks.json"
    tasks = [
        {"id": 1, "description": "Task one", "done": False},
        {"id": 2, "description": "Task two", "done": True},
        {"id": 3, "description": "Task three", "done": False},
    ]
    tasks_file.write_text(json.dumps(tasks))

    delete_task(2)

    remaining = json.loads(tasks_file.read_text())
    assert len(remaining) == 2
    assert remaining[0]["id"] == 1
    assert remaining[1]["id"] == 2
    assert remaining[0]["description"] == "Task one"
    assert remaining[1]["description"] == "Task three"


def test_delete_task_not_found(tmp_path, monkeypatch, capsys):
    """Test deleting with invalid ID shows error."""
    from commands import delete as delete_module
    monkeypatch.setattr(delete_module, "get_tasks_file", lambda: tmp_path / "tasks.json")

    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(json.dumps([{"id": 1, "description": "Only task", "done": False}]))

    delete_task(99)

    captured = capsys.readouterr()
    assert "Invalid task ID" in captured.out or "Task 99 not found" in captured.out


def test_delete_task_empty(tmp_path, monkeypatch, capsys):
    """Test deleting from empty task list."""
    from commands import delete as delete_module
    monkeypatch.setattr(delete_module, "get_tasks_file", lambda: tmp_path / "tasks.json")

    tasks_file = tmp_path / "tasks.json"
    tasks_file.write_text(json.dumps([]))

    delete_task(1)

    captured = capsys.readouterr()
    assert "No tasks" in captured.out