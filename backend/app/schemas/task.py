from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from .user import UserResponse

class TaskBase(BaseModel):
    column_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    priority: int = 2  # Изменено с str на int
    budget: Optional[float] = None
    due_date: Optional[datetime] = None
    tags: List[str] = []

    @validator('priority', pre=True)
    def convert_priority_to_int(cls, v):
        if v is None:
            return 2  # default to medium
        if isinstance(v, str):
            priority_map = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "urgent": 4
            }
            return priority_map.get(v.lower(), 2)  # default to medium
        return v

    @validator('tags', pre=True)
    def convert_tags_to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            if v == '' or v == '{}':
                return []
            # Пытаемся парсить как JSON
            try:
                import json
                return json.loads(v)
            except:
                # Если не JSON, разделяем по запятой
                return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

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
    priority: Optional[int] = None  # Изменено с str на int
    column_id: Optional[int] = None
    budget: Optional[float] = None
    due_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    assigned_to_id: Optional[int] = None
    parent_id: Optional[int] = None

    @validator('priority', pre=True)
    def convert_priority_to_int(cls, v):
        if v is None:
            return None
        if isinstance(v, str):
            priority_map = {
                "low": 1,
                "medium": 2,
                "high": 3,
                "urgent": 4
            }
            return priority_map.get(v.lower(), 2)  # default to medium
        return v

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

class TaskResponse(BaseModel):
    id: int
    title: str
    column_id: Optional[int] = None
    board_id: Optional[int] = None
    assigned_to_id: Optional[int] = None
    creator_id: int
    parent_id: Optional[int] = None
    rating: Optional[float] = None
    tags: List[str]
    budget: Optional[float]
    priority: str
    description: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

    @validator('priority', pre=True)
    def convert_int_to_priority_string(cls, v):
        if isinstance(v, int):
            priority_map = {
                1: "low",
                2: "medium", 
                3: "high",
                4: "urgent"
            }
            return priority_map.get(v, "medium")
        return v

    @validator('tags', pre=True)
    def convert_tags_to_list(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            if v == '' or v == '{}':
                return []
            # Пытаемся парсить как JSON
            try:
                import json
                return json.loads(v)
            except:
                # Если не JSON, разделяем по запятой
                return [tag.strip() for tag in v.split(',') if tag.strip()]
        return v

class TaskWithRelations(TaskResponse):
    assigned_to: Optional[UserResponse] = None
    created_by: UserResponse
    parent: Optional["TaskWithRelations"] = None
    subtasks: List["TaskWithRelations"] = [] 