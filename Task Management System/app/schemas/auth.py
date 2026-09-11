from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.security import validate_password_strength
from app.schemas.user import UserOut


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserRegister(BaseModel):
    email: EmailStr = "user@gmail.com"
    name: str = Field(..., min_length=1)
    password: str = "Strong@123"
    phone: str | None = None
    role: UserRole = UserRole.USER

    @field_validator("phone")
    def phone_must_be_digits(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return v

    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        return validate_password_strength(v)


class UserLogin(BaseModel):
    email: EmailStr = "admin@gmail.com"
    password: str = "Strong@123"


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class ChangePassword(BaseModel):
    current_password: str | None = None
    new_password: str

    @field_validator("new_password")
    def validate_new_password(cls, v: str) -> str:
        return validate_password_strength(v)


class ChangePasswordResponse(BaseModel):
    message: str = Field(..., json_schema_extra={"example": "Password changed successfully"})


class UpdateProfile(BaseModel):
    email: EmailStr | None = None
    name: str | None = Field(None, min_length=1, max_length=100)
    phone: str | None = None

    @field_validator("phone")
    def phone_must_be_digits(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not v.isdigit() or len(v) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        return v