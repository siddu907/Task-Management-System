from datetime import datetime
from enum import Enum
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from app.core.security import validate_password_strength

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr = "user@gmail.com"
    phone: str | None = None
    role: UserRole = UserRole.USER
    password: str = "Strong@123"

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
    
    
class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: str
    phone: str | None = None
    is_active: bool
    created_at: datetime

class UserUpdate(BaseModel):
    email: EmailStr | None = Field(None, json_schema_extra={"example": "user@gmail.com"})
    full_name: str | None = None
    phone: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None
    

    @field_validator("full_name")
    def validate_full_name(cls, value: str) -> str:
        if value is not None and not value.strip():
            raise ValueError("Full name must not be blank")
        return value

    @field_validator("phone")
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and (not value.isdigit() or len(value) != 10):
            raise ValueError("Phone number must be exactly 10 digits and contain only numbers")
        return value

