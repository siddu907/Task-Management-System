from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.core.security import create_access_token, hash_password, revoke_user_tokens, verify_password
from app.database import get_db
from app.models.user import User
from app.schemas.auth import AuthResponse, ChangePassword, UpdateProfile, UserLogin, UserRegister
from app.schemas.user import UserOut
from app.services.auth_service import AuthenticationError, authenticate_user, register_user

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=201)
def register(payload: UserRegister, db: Session = Depends(get_db)):
    try:
        user = register_user(
            db,
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            password=payload.password,
            role="user",
        )
    except AuthenticationError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, str(exc)) from exc

    token = create_access_token(user.id, role=user.role)
    return AuthResponse(access_token=token, user=user)


@router.post("/login", response_model=AuthResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        user, token = authenticate_user(db, email=payload.email, password=payload.password)
    except AuthenticationError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(exc)) from exc

    return AuthResponse(access_token=token, user=user)


@router.post("/logout")
def logout(user: User = Depends(get_current_user)):
    revoke_user_tokens(user.id)
    return {"message": "Logged out successfully"}


@router.get("/profile", response_model=UserOut)
def profile(user: User = Depends(get_current_user)):
    return user


@router.put("/profile", response_model=UserOut)
def update_profile(payload: UpdateProfile, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.name is not None:
        user.name = payload.name.strip()

    if payload.phone is not None:
        user.phone = payload.phone

    if payload.email is not None:
        existing = db.query(User).filter(User.email == str(payload.email).lower(), User.id != user.id).first()
        if existing is not None:
            raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered")
        user.email = str(payload.email).strip().lower()

    db.commit()
    db.refresh(user)
    return user


@router.put("/change-password")
def change_password(payload: ChangePassword, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if payload.current_password is not None and not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Current password is incorrect")
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    revoke_user_tokens(user.id)
    return {"message": "Password changed successfully"}
