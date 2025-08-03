from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    order_id: int
    receiver_id: int

class MessageUpdate(BaseModel):
    content: Optional[str] = None
    is_read: Optional[bool] = None

class MessageResponse(MessageBase):
    id: int
    order_id: int
    sender_id: int
    receiver_id: int
    is_read: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class MessageWithUsers(MessageResponse):
    sender_name: str
    receiver_name: str 