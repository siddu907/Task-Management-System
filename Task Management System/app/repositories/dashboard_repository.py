from datetime import datetime

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.task import Task
from app.models.user import User


class DashboardRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_users(self) -> int:
        return self.db.scalar(select(func.count(User.id))) or 0

    def count_tasks(self) -> int:
        return self.db.scalar(select(func.count(Task.id))) or 0

    def count_status(self, status: str) -> int:
        return self.db.scalar(select(func.count(Task.id)).where(Task.status == status)) or 0

    def count_priority(self, priority: str) -> int:
        return self.db.scalar(select(func.count(Task.id)).where(Task.priority == priority)) or 0

    def count_overdue(self, now: datetime) -> int:
        return self.db.scalar(
            select(func.count(Task.id)).where(
                Task.due_date < now,
                Task.status.not_in(("completed", "cancelled")),
            )
        ) or 0

    def list_user_tasks(self, user_id: int) -> list[Task]:
        return list(self.db.scalars(select(Task).where(or_(Task.assigned_to_id == user_id, Task.created_by_id == user_id))).all())
