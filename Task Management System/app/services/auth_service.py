from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthenticationError(Exception):
    pass


def register_user(db: Session, *, name: str, email: str, phone: str | None, password: str, role: str = "user") -> User:
    repository = UserRepository(db)
    normalized_email = email.strip().lower()
    if repository.get_by_email(normalized_email):
        raise AuthenticationError("Email is already registered")

    user = User(
        name=name,
        email=normalized_email,
        phone=phone,
        role=role,
        password_hash=hash_password(password),
    )
    repository.add(user)
    repository.save()
    db.refresh(user)
    return user


def authenticate_user(db: Session, *, email: str, password: str) -> tuple[User, str]:
    user = UserRepository(db).get_by_email(email)
    if user is None or not user.is_active:
        raise AuthenticationError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Invalid email or password")

    token = create_access_token(user.id, user.role)
    return user, token
