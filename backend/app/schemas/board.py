from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from .user import UserResponse
from .task import TaskResponse
from .column import ColumnResponse

class BoardBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = True

class BoardCreate(BoardBase):
    pass

class BoardUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class BoardResponse(BoardBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class BoardWithTasks(BoardResponse):
    creator: UserResponse  # Изменено с owner на creator
    tasks: List[TaskResponse] = [] 
    columns: List[ColumnResponse]