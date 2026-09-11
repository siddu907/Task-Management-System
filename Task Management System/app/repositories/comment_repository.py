from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.comment import Comment


class CommentRepository:
	def __init__(self, db: Session):
		self.db = db

	def get(self, comment_id: int) -> Comment | None:
		return self.db.get(Comment, comment_id)

	def list_for_task(self, task_id: int) -> list[Comment]:
		return list(self.db.scalars(select(Comment).where(Comment.task_id == task_id).order_by(Comment.created_at)).all())

	def add(self, comment: Comment) -> Comment:
		self.db.add(comment)
		self.db.flush()
		return comment

	def save(self) -> None:
		self.db.commit()

	def delete(self, comment: Comment) -> None:
		self.db.delete(comment)
