from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum

class ProposalStatus(enum.Enum):
    PENDING = "pending"     # Ожидает рассмотрения
    ACCEPTED = "accepted"   # Принято
    REJECTED = "rejected"   # Отклонено
    WITHDRAWN = "withdrawn" # Отозвано

class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(Integer, primary_key=True, index=True)
    message = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    estimated_duration = Column(Integer, nullable=True)  # в днях
    status = Column(Enum(ProposalStatus), default=ProposalStatus.PENDING)
    
    # Foreign Keys
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    executor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    order = relationship("Order", back_populates="proposals")
    executor = relationship("User", foreign_keys=[executor_id], back_populates="proposals") 