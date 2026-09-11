from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.dependencies import require_roles
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut, UserUpdate
from app.services.notification_service import record_audit
from app.services.user_service import create_managed_user, get_user as find_user, list_users as find_users, update_user as save_user

router = APIRouter()
admin = require_roles("admin")


@router.get("", response_model=list[UserOut])
def list_users(_: User = Depends(admin), db: Session = Depends(get_db)):
	return find_users(db)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, _: User = Depends(admin), db: Session = Depends(get_db)):
	user = find_user(db, user_id)
	if user is None:
		raise HTTPException(404, "User not found")
	return user


@router.post("", response_model=UserOut, status_code=201)
def create_user(payload: UserCreate, background_tasks: BackgroundTasks, current_user: User = Depends(admin), db: Session = Depends(get_db)):
	try:
		user = create_managed_user(db, name=payload.name, email=payload.email, phone=payload.phone,
								 password=payload.password, role=payload.role.value)
	except ValueError as exc:
		raise HTTPException(409, str(exc)) from exc
	background_tasks.add_task(record_audit, current_user.id, "User Created", "user", user.id)
	return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, background_tasks: BackgroundTasks, current_user: User = Depends(admin), db: Session = Depends(get_db)):
	user = find_user(db, user_id)
	if user is None:
		raise HTTPException(404, "User not found")
	values = payload.model_dump(exclude_unset=True)
	if "full_name" in values:
		values["name"] = values.pop("full_name")
	if "role" in values:
		values["role"] = values["role"].value
	try:
		user = save_user(db, user, values)
	except ValueError as exc:
		raise HTTPException(409, str(exc)) from exc
	background_tasks.add_task(record_audit, current_user.id, "User Updated", "user", user.id)
	return user


@router.delete("/{user_id}")
def delete_user(user_id: int, background_tasks: BackgroundTasks, current_user: User = Depends(admin), db: Session = Depends(get_db)):
	user = find_user(db, user_id)
	if user is None:
		raise HTTPException(404, "User not found")
	save_user(db, user, {"is_active": False})
	background_tasks.add_task(record_audit, current_user.id, "User Deactivated", "user", user.id)
	return {"message": "User deactivated"}
