from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    role: Optional[str] = "analyst"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
