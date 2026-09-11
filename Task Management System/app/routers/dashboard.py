from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services.dashboard_service import admin_metrics, user_metrics

router = APIRouter()

@router.get("/admin")
def admin_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	if user.role != "admin": from fastapi import HTTPException; raise HTTPException(403, "Admin access required")
	return admin_metrics(db)

@router.get("/user")
def user_dashboard(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
	return user_metrics(db, user)
