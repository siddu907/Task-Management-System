from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.task import Task


class TaskRepository:
	def __init__(self, db: Session):
		self.db = db

	def get(self, task_id: int) -> Task | None:
		return self.db.get(Task, task_id)

	def list_for_user(self, user_id: int, role: str, *, status: str | None = None,
					  priority: str | None = None, assigned_user_id: int | None = None,
					  search: str | None = None, sort_by: str = "created_at", sort_order: str = "desc",
					  offset: int = 0, limit: int = 20) -> list[Task]:
		query = select(Task)
		if role != "admin":
			query = query.where(or_(Task.created_by_id == user_id, Task.assigned_to_id == user_id))
		if status:
			query = query.where(Task.status == status)
		if priority:
			query = query.where(Task.priority == priority)
		if assigned_user_id:
			query = query.where(Task.assigned_to_id == assigned_user_id)
		if search:
			query = query.where(or_(Task.title.ilike(f"%{search}%"), Task.description.ilike(f"%{search}%")))
		sort_column = getattr(Task, sort_by)
		ordering = sort_column.asc() if sort_order == "asc" else sort_column.desc()
		return list(self.db.scalars(query.order_by(ordering).offset(offset).limit(limit)).all())

	def add(self, task: Task) -> Task:
		self.db.add(task)
		self.db.flush()
		return task

	def save(self) -> None:
		self.db.commit()

	def delete(self, task: Task) -> None:
		self.db.delete(task)
