import pytest

from app.models.task import Task
from app.services.task_service import VALID_TRANSITIONS, change_task_status


def test_status_transition_service():
    task = Task(title="Service task", created_by_id=1, status="todo")
    change_task_status(task, "in_progress")
    assert task.status == "in_progress"
    change_task_status(task, "completed")
    assert task.completed_at is not None
    with pytest.raises(ValueError):
        change_task_status(task, "todo")
    assert VALID_TRANSITIONS["cancelled"] == set()
