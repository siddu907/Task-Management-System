from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


def normalize_email(email: str) -> str:
	return email.strip().lower()


def ensure_active_user(db: Session, user_id: int) -> User:
	user = UserRepository(db).get(user_id)
	if user is None or not user.is_active:
		raise ValueError("User does not exist or is inactive")
	return user


def deactivate_user(db: Session, user_id: int) -> User:
	user = UserRepository(db).get(user_id)
	if user is None:
		raise ValueError("User not found")
	user.is_active = False
	db.commit()
	return user


def update_user_password(db: Session, user: User, new_password: str) -> None:
	user.password_hash = hash_password(new_password)
	db.commit()


def list_users(db: Session) -> list[User]:
	return UserRepository(db).list()


def get_user(db: Session, user_id: int) -> User | None:
	return UserRepository(db).get(user_id)


def create_managed_user(db: Session, *, name: str, email: str, phone: str | None, password: str, role: str) -> User:
	repository = UserRepository(db)
	normalized_email = normalize_email(email)
	if repository.get_by_email(normalized_email):
		raise ValueError("Email is already registered")
	user = User(name=name, email=normalized_email, phone=phone, role=role, password_hash=hash_password(password))
	repository.add(user)
	repository.save()
	db.refresh(user)
	return user


def update_user(db: Session, user: User, values: dict) -> User:
	if "email" in values:
		normalized_email = normalize_email(values["email"])
		existing_user = UserRepository(db).get_by_email(normalized_email)
		if existing_user is not None and existing_user.id != user.id:
			raise ValueError("Email is already registered")
		values["email"] = normalized_email
	for key, value in values.items():
		setattr(user, key, value)
	db.commit()
	db.refresh(user)
	return user
