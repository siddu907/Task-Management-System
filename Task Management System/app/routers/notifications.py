from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationOut
from app.repositories.notification_repository import NotificationRepository

router = APIRouter()

@router.get("", response_model=list[NotificationOut])
def list_notifications(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return NotificationRepository(db).list_for_user(user.id)

@router.put("/{notification_id}/read", response_model=NotificationOut)
def mark_read(notification_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	notification = NotificationRepository(db).get_for_user(notification_id, user.id)
	if notification is None: raise HTTPException(404, "Notification not found")
	notification.is_read = True; db.commit(); db.refresh(notification)
	return notification

@router.put("/read-all")
def mark_all_read(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	for notification in NotificationRepository(db).list_for_user(user.id):
		if not notification.is_read:
			notification.is_read = True
	db.commit(); return {"message": "Notifications marked as read"}
