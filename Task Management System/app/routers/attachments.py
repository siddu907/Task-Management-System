from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from app.config import settings
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.attachment import Attachment
from app.models.task import Task
from app.models.user import User
from app.schemas.attachment import AttachmentOut
from app.repositories.attachment_repository import AttachmentRepository
from app.services.attachment_service import remove_attachment, save_attachment

router = APIRouter()
ALLOWED = {"pdf", "jpg", "jpeg", "png", "doc", "docx", "txt"}


def get_task(task_id: int, user: User, db: Session) -> Task:
	from app.services.task_service import get_task as find_task
	task = find_task(db, task_id)
	if task is None: raise HTTPException(404, "Task not found")
	if user.role != "admin" and task.created_by_id != user.id and task.assigned_to_id != user.id: raise HTTPException(403, "Not authorized")
	return task


@router.post("/tasks/{task_id}/attachments", response_model=AttachmentOut, status_code=201)
async def upload_attachment(task_id: int, file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	task = get_task(task_id, user, db)
	suffix = Path(file.filename or "").suffix.lower().lstrip(".")
	if suffix not in ALLOWED: raise HTTPException(400, "Unsupported file type")
	content = await file.read()
	if len(content) > settings.max_upload_size_bytes: raise HTTPException(413, "File exceeds maximum size")
	directory = Path(settings.upload_directory); directory.mkdir(parents=True, exist_ok=True)
	stored = directory / f"{uuid4().hex}.{suffix}"
	stored.write_bytes(content)
	attachment = Attachment(task_id=task.id, file_name=file.filename, file_path=str(stored), file_type=file.content_type or suffix, file_size=len(content))
	return save_attachment(db, attachment)


@router.get("/tasks/{task_id}/attachments", response_model=list[AttachmentOut])
def list_attachments(task_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	get_task(task_id, user, db)
	return AttachmentRepository(db).list_for_task(task_id)


@router.delete("/attachments/{attachment_id}")
def delete_attachment(attachment_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	attachment = db.get(Attachment, attachment_id)
	if attachment is None: raise HTTPException(404, "Attachment not found")
	get_task(attachment.task_id, user, db)
	remove_attachment(db, attachment)
	return {"message": "Attachment deleted"}
