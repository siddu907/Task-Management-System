from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog


class AuditRepository:
	def __init__(self, db: Session):
		self.db = db

	def get(self, log_id: int) -> AuditLog | None:
		return self.db.get(AuditLog, log_id)

	def list(self, *, limit: int | None = None, offset: int = 0) -> list[AuditLog]:
		query = select(AuditLog).order_by(AuditLog.timestamp.desc()).offset(offset)
		if limit is not None:
			query = query.limit(limit)
		return list(self.db.scalars(query).all())

	def add(self, log: AuditLog) -> AuditLog:
		self.db.add(log)
		self.db.flush()
		return log

	def save(self) -> None:
		self.db.commit()
