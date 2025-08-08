from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class OrderStatus(enum.Enum):
    OPEN = "open"           # Открыт для предложений
    IN_PROGRESS = "in_progress"  # В работе
    COMPLETED = "completed"      # Завершен
    CANCELLED = "cancelled"      # Отменен

class OrderPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(Float, nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=False)
    priority = Column(String(20), default=OrderPriority.MEDIUM.value)
    status = Column(String(20), default=OrderStatus.OPEN.value)
    tags = Column(String, nullable=True)  # JSON строка с тегами
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_executor_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_orders")
    assigned_executor = relationship("User", foreign_keys=[assigned_executor_id])
    proposals = relationship("Proposal", back_populates="order", cascade="all, delete-orphan")
    # messages = relationship("Message", back_populates="order", cascade="all, delete-orphan") 