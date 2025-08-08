from pydantic import BaseModel, validator
from typing import Optional, Any
from datetime import datetime
from enum import Enum

class ProposalStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class ProposalBase(BaseModel):
    description: str  # Изменено с message на description
    price: float
    estimated_duration: Optional[int] = None

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('estimated_duration')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Estimated duration must be positive')
        return v

class ProposalCreate(ProposalBase):
    order_id: int

class ProposalUpdate(BaseModel):
    description: Optional[str] = None  # Изменено с message на description
    price: Optional[float] = None
    estimated_duration: Optional[int] = None
    status: Optional[ProposalStatus] = None

    @validator('price')
    def validate_price(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Price must be positive')
        return v

    @validator('estimated_duration')
    def validate_duration(cls, v):
        if v is not None and v <= 0:
            raise ValueError('Estimated duration must be positive')
        return v

class ProposalResponse(ProposalBase):
    id: int
    order_id: int
    user_id: int
    status: ProposalStatus
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ProposalWithExecutor(ProposalResponse):
    executor: Any

class ProposalWithOrder(ProposalResponse):
    order: Any

class ProposalStats(BaseModel):
    total_proposals: int
    pending_proposals: int
    accepted_proposals: int
    rejected_proposals: int
    average_price: float

# Модели будут обновлены при использовании 