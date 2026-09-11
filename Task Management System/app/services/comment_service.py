from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.task import Task
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.services.task_service import can_access_task


def validate_comment_access(task: Task, user: User) -> None:
	if not can_access_task(task, user):
		raise PermissionError("Not authorized to access this task")
	if task.status in {"completed", "cancelled"}:
		raise ValueError("Closed tasks cannot receive comments")


def add_comment(db: Session, task: Task, user: User, content: str) -> Comment:
	validate_comment_access(task, user)
	comment = Comment(task_id=task.id, user_id=user.id, content=content)
	CommentRepository(db).add(comment)
	db.commit()
	db.refresh(comment)
	return comment


def can_modify_comment(comment: Comment, user: User) -> bool:
	return user.role == "admin" or comment.user_id == user.id
