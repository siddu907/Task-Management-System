from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from app.config import settings

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
TOKEN_VERSIONS: dict[int, int] = {}


def validate_password_strength(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(char.islower() for char in password):
        raise ValueError("Password must contain at least one lowercase letter")
    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit")
    if not any(not char.isalnum() for char in password):
        raise ValueError("Password must contain at least one special character")
    return password


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def revoke_user_tokens(user_id: int) -> None:
    user_id = int(user_id)
    TOKEN_VERSIONS[user_id] = TOKEN_VERSIONS.get(user_id, 0) + 1


def create_access_token(subject: str | int | dict, role: str | None = None, expires_delta: timedelta | None = None) -> str:
    if isinstance(subject, dict):
        payload = dict(subject)
    else:
        payload = {"sub": str(subject)}

    user_id = None
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        user_id = None

    if user_id is not None:
        payload["ver"] = TOKEN_VERSIONS.get(user_id, 0)

    if role is not None:
        payload["role"] = role

    if "exp" not in payload:
        delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
        payload["exp"] = datetime.now(timezone.utc) + delta

    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str):
    payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    subject = payload.get("sub")
    try:
        user_id = int(subject) if subject is not None else None
    except (TypeError, ValueError):
        user_id = None

    if user_id is not None:
        current_version = TOKEN_VERSIONS.get(user_id, 0)
        token_version = int(payload.get("ver", 0))
        if token_version < current_version:
            raise ValueError("Token revoked")

    return payload
