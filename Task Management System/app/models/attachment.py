from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Attachment(Base):
    __tablename__ = "attachments"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"),nullable=False)
    file_name: Mapped[str] = mapped_column(String(255),nullable=False)
    file_path: Mapped[str] = mapped_column(String(500),nullable=False)
    file_type: Mapped[str] = mapped_column(String(100),nullable=False)
    file_size: Mapped[int] = mapped_column(nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)
    task = relationship("Task",back_populates="attachments")