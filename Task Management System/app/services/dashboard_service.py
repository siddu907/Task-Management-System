from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.dashboard_repository import DashboardRepository


def admin_metrics(db: Session) -> dict[str, int]:
    repository = DashboardRepository(db)
    return {
        "total_users": repository.count_users(),
        "total_tasks": repository.count_tasks(),
        "open_tasks": repository.count_status("todo"),
        "in_progress_tasks": repository.count_status("in_progress"),
        "completed_tasks": repository.count_status("completed"),
        "critical_tasks": repository.count_priority("critical"),
        "overdue_tasks": repository.count_overdue(datetime.now(timezone.utc).replace(tzinfo=None)),
    }


def user_metrics(db: Session, user: User) -> dict[str, int]:
    tasks = DashboardRepository(db).list_user_tasks(user.id)
    return {
        "my_tasks": len(tasks),
        "pending_tasks": sum(task.status in {"todo", "in_progress"} for task in tasks),
        "completed_tasks": sum(task.status == "completed" for task in tasks),
        "overdue_tasks": sum(task.due_date is not None and task.due_date < datetime.now(timezone.utc).replace(tzinfo=None) and task.status not in {"completed", "cancelled"} for task in tasks),
        "critical_tasks": sum(task.priority == "critical" for task in tasks),
    }