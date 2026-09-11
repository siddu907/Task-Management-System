from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.attachment import Attachment


class AttachmentRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, attachment_id: int) -> Attachment | None:
        return self.db.get(Attachment, attachment_id)

    def list_for_task(self, task_id: int) -> list[Attachment]:
        return list(self.db.scalars(select(Attachment).where(Attachment.task_id == task_id)).all())

    def add(self, attachment: Attachment) -> Attachment:
        self.db.add(attachment)
        self.db.flush()
        return attachment

    def delete(self, attachment: Attachment) -> None:
        self.db.delete(attachment)

    def save(self) -> None:
        self.db.commit()