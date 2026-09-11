from datetime import datetime, timezone
from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"),nullable=True)
    action: Mapped[str] = mapped_column(String(100),nullable=False)
    entity_type: Mapped[str] = mapped_column(String(50),nullable=False)
    entity_id: Mapped[int | None] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime,default=lambda: datetime.now(timezone.utc),nullable=False)
    user = relationship("User", back_populates="audit_logs")