from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    confirm_password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    is_verified: bool = False
    last_login: Optional[datetime] = None

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str

class TokenData(BaseModel):
    user_id: str
    email: str 