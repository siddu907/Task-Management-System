from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)
    task_id: Mapped[int | None] = mapped_column(ForeignKey("tasks.id"),nullable=True)
    message: Mapped[str] = mapped_column(Text,nullable=False)
    notification_type: Mapped[str] = mapped_column(String(50),nullable=False)
    is_read: Mapped[bool] = mapped_column(Boolean,default=False,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)
    user = relationship("User",back_populates="notifications")
    task = relationship("Task",back_populates="notifications")