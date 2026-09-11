from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import require_roles
from app.database import get_db
from app.models.user import User
from app.repositories.audit_repository import AuditRepository
from app.schemas.audit_log import AuditLogOut

router = APIRouter()

@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(_: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
	return AuditRepository(db).list()

@router.get("/{log_id}", response_model=AuditLogOut)
def get_audit_log(log_id: int, _: User = Depends(require_roles("admin")), db: Session = Depends(get_db)):
	log = AuditRepository(db).get(log_id)
	if log is None: raise HTTPException(404, "Audit log not found")
	return log
