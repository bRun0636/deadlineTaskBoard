from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class TaskBase(BaseModel):
    column_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    budget: Optional[float] = None
    due_date: Optional[datetime] = None
    tags: List[str] = []

    @validator('due_date', pre=True)
    def parse_due_date(cls, v):
        if v is None or v == '' or v == 'null':
            return None
        if isinstance(v, str):
            try:
                # Убираем лишние символы и пробелы
                v = v.strip()
                if not v:
                    return None
                # Пробуем ISO формат
                dt = datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Пробуем формат YYYY-MM-DDTHH:MM
                    dt = datetime.strptime(v, '%Y-%m-%dT%H:%M')
                except ValueError:
                    try:
                        # Пробуем формат YYYY-MM-DD
                        dt = datetime.strptime(v, '%Y-%m-%d')
                    except ValueError:
                        raise ValueError('Invalid date format. Use ISO format, YYYY-MM-DDTHH:MM, or YYYY-MM-DD')
            
            # Проверяем, что год разумный
            if dt.year < 1900 or dt.year > 2100:
                raise ValueError(f'Year {dt.year} is out of reasonable range (1900-2100)')
            
            return dt
        return v

class TaskCreate(TaskBase):
    board_id: int
    assigned_to_id: Optional[int] = None
    parent_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    column_id: Optional[int] = None
    budget: Optional[float] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    assigned_to_id: Optional[int] = None
    parent_id: Optional[int] = None

    @validator('due_date', pre=True)
    def parse_due_date(cls, v):
        if v is None or v == '':
            return None
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                try:
                    return datetime.strptime(v, '%Y-%m-%dT%H:%M')
                except ValueError:
                    raise ValueError('Invalid date format. Use ISO format or YYYY-MM-DDTHH:MM')
        return v

class TaskStatusUpdate(BaseModel):
    column_id: Optional[int] = None

class TaskResponse(TaskBase):
    id: int
    title: str
    column_id: Optional[int] = None
    board_id: int
    assigned_to_id: Optional[int] = None
    created_by_id: int
    parent_id: Optional[int] = None
    rating: Optional[float] = None
    tags: List[str]
    budget: Optional[float]
    priority: str
    description: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class TaskWithRelations(TaskResponse):
    assigned_to: Optional[UserResponse] = None
    created_by: UserResponse
    parent: Optional["TaskWithRelations"] = None
    subtasks: List["TaskWithRelations"] = [] 