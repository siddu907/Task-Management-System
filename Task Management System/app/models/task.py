from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    title: Mapped[str] = mapped_column(String(200),nullable=False)
    description: Mapped[str | None] = mapped_column(Text,nullable=True)
    assigned_to_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"),nullable=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    priority: Mapped[str] = mapped_column(String(20),default="medium",nullable=False)
    status: Mapped[str] = mapped_column(String(20),default="todo",nullable=False)
    due_date: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),onupdate=lambda: datetime.now(timezone.utc),nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime,nullable=True)
    assigned_to = relationship("User",foreign_keys=[assigned_to_id],back_populates="assigned_tasks")
    created_by = relationship("User",foreign_keys=[created_by_id],back_populates="created_tasks")
    comments = relationship("Comment", back_populates="task",cascade="all, delete-orphan")
    attachments = relationship( "Attachment",back_populates="task",cascade="all, delete-orphan")
    notifications = relationship("Notification",back_populates="task")