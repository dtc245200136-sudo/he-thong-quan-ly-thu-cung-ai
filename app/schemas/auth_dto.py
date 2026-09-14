from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    full_name: str
    role: str = "STAFF" # ADMIN, RECEPTIONIST, STAFF
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    full_name: str
    role: Optional[str] = "STAFF"
    phone: Optional[str] = None
    email: Optional[str] = None

class ResetPasswordRequest(BaseModel):
    username: str
    verify_info: Optional[str] = None  # email hoặc số điện thoại để xác minh
    new_password: str

