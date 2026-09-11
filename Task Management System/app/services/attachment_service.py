from pathlib import Path

from sqlalchemy.orm import Session

from app.models.attachment import Attachment
from app.repositories.attachment_repository import AttachmentRepository


def save_attachment(db: Session, attachment: Attachment) -> Attachment:
    repository = AttachmentRepository(db)
    repository.add(attachment)
    repository.save()
    db.refresh(attachment)
    return attachment


def remove_attachment(db: Session, attachment: Attachment) -> None:
    Path(attachment.file_path).unlink(missing_ok=True)
    repository = AttachmentRepository(db)
    repository.delete(attachment)
    repository.save()