from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, nullable=False)  # Внешний ключ определен в базе данных
    sender_id = Column(Integer, nullable=False)  # Внешний ключ определен в базе данных
    receiver_id = Column(Integer, nullable=True)  # Внешний ключ определен в базе данных
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Отношения (добавляются после загрузки всех моделей)
    # order = relationship("Order", back_populates="messages")
    # sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    # receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages") 