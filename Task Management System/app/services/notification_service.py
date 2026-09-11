from app.database import SessionLocal
from app.models.notification import Notification
from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository
from app.repositories.notification_repository import NotificationRepository


def create_notification(user_id: int, message: str, notification_type: str, task_id: int | None = None) -> None:
	db = SessionLocal()
	try:
		repository = NotificationRepository(db)
		repository.add(Notification(user_id=user_id, task_id=task_id, message=message, notification_type=notification_type))
		repository.save()
	finally:
		db.close()


def record_audit(user_id: int, action: str, entity_type: str, entity_id: int | None = None) -> None:
	db = SessionLocal()
	try:
		repository = AuditRepository(db)
		repository.add(AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id))
		repository.save()
	finally:
		db.close()
