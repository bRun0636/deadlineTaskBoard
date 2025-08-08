from pydantic import BaseModel, validator
from typing import Optional, List, Any, ForwardRef
from datetime import datetime, timezone
from enum import Enum

# Forward references для избежания циклических импортов
ProposalResponse = ForwardRef("ProposalResponse")

class OrderStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class OrderPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class OrderBase(BaseModel):
    title: str
    description: str
    budget: float
    deadline: datetime
    priority: OrderPriority = OrderPriority.MEDIUM
    tags: Optional[str] = None

    @validator('budget')
    def validate_budget(cls, v):
        if v <= 0:
            raise ValueError('Budget must be positive')
        return v

    @validator('deadline')
    def validate_deadline(cls, v):
        if v <= datetime.now(timezone.utc):
            raise ValueError('Deadline must be in the future')
        return v

class OrderCreate(OrderBase):
    pass

class OrderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[float] = None
    deadline: Optional[datetime] = None
    priority: Optional[OrderPriority] = None
    status: Optional[OrderStatus] = None
    tags: Optional[str] = None
    assigned_executor_id: Optional[int] = None

    @validator('budget')
    def validate_budget(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Budget must be positive')
        return v

    @validator('deadline')
    def validate_deadline(cls, v):
        if v is not None and v <= datetime.now(timezone.utc):
            raise ValueError('Deadline must be in the future')
        return v

class OrderResponse(OrderBase):
    id: int
    creator_id: int  # Изменено с customer_id на creator_id
    assigned_executor_id: Optional[int] = None
    status: OrderStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }

class OrderWithCustomer(OrderResponse):
    customer: Any

class OrderWithProposals(OrderResponse):
    proposals: List["ProposalResponse"] = []

class OrderStats(BaseModel):
    total_orders: int
    open_orders: int
    in_progress_orders: int
    completed_orders: int
    total_budget: float
    average_budget: float

# Обновляем forward references
from .proposal import ProposalResponse
OrderWithProposals.model_rebuild() 