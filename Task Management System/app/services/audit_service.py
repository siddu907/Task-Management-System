from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.repositories.audit_repository import AuditRepository


def record_audit(db: Session, *, user_id: int | None, action: str, entity_type: str, entity_id: int | None = None) -> AuditLog:
	log = AuditLog(user_id=user_id, action=action, entity_type=entity_type, entity_id=entity_id)
	repository = AuditRepository(db)
	repository.add(log)
	repository.save()
	db.refresh(log)
	return log
