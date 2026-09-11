from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.notification import Notification


class NotificationRepository:
	def __init__(self, db: Session):
		self.db = db

	def list_for_user(self, user_id: int) -> list[Notification]:
		return list(self.db.scalars(select(Notification).where(Notification.user_id == user_id).order_by(Notification.created_at.desc())).all())

	def get_for_user(self, notification_id: int, user_id: int) -> Notification | None:
		return self.db.scalar(select(Notification).where(Notification.id == notification_id, Notification.user_id == user_id))

	def add(self, notification: Notification) -> Notification:
		self.db.add(notification)
		self.db.flush()
		return notification

	def save(self) -> None:
		self.db.commit()
