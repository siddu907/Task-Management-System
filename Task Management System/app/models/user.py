from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255),unique=True,index=True,nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20),default="user",nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)
    created_tasks = relationship("Task",foreign_keys="Task.created_by_id",back_populates="created_by")
    assigned_tasks = relationship("Task",foreign_keys="Task.assigned_to_id",back_populates="assigned_to")
    comments = relationship("Comment",back_populates="user")
    notifications = relationship("Notification",back_populates="user")
    audit_logs = relationship("AuditLog",back_populates="user")