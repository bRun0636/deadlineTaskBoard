from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(UserBase):
    id: int
    rating: float
    completed_tasks: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserWithBoards(UserResponse):
    boards: List["BoardResponse"] = []

class UserAdminUpdate(BaseModel):
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None

class SystemStats(BaseModel):
    total_users: int
    active_users: int
    total_boards: int
    active_boards: int
    total_tasks: int
    completed_tasks: int
    superusers: int 