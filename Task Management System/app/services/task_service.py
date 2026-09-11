from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User
from app.repositories.task_repository import TaskRepository
from app.services.user_service import ensure_active_user

VALID_TRANSITIONS: dict[str, set[str]] = {
	"todo": {"in_progress", "cancelled"},
	"in_progress": {"todo", "completed", "cancelled"},
	"completed": set(),
	"cancelled": set(),
}


def can_access_task(task: Task, user: User) -> bool:
	return user.role == "admin" or task.created_by_id == user.id or task.assigned_to_id == user.id


def validate_task_assignment(db: Session, assigned_to_id: int | None) -> None:
	if assigned_to_id is not None:
		ensure_active_user(db, assigned_to_id)


def change_task_status(task: Task, new_status: str) -> None:
	if new_status not in VALID_TRANSITIONS.get(task.status, set()):
		raise ValueError("Invalid status transition")
	task.status = new_status
	task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None) if new_status == "completed" else None


def save_task(db: Session, task: Task) -> Task:
	TaskRepository(db).add(task)
	db.commit()
	db.refresh(task)
	return task


def get_task(db: Session, task_id: int) -> Task | None:
	return TaskRepository(db).get(task_id)


def list_tasks(db: Session, user: User, *, status: str | None = None, priority: str | None = None,
			   assigned_user_id: int | None = None, search: str | None = None, sort_by: str = "created_at",
			   sort_order: str = "desc", offset: int = 0, limit: int = 20) -> list[Task]:
	return TaskRepository(db).list_for_user(user.id, user.role, status=status, priority=priority,
										 assigned_user_id=assigned_user_id, search=search, sort_by=sort_by,
										 sort_order=sort_order, offset=offset, limit=limit)


def delete_task(db: Session, task: Task) -> None:
	repository = TaskRepository(db)
	repository.delete(task)
	repository.save()
