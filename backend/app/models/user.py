from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from passlib.context import CryptContext
import enum

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserRole(enum.Enum):
    CUSTOMER = "customer"  # Заказчик
    EXECUTOR = "executor"  # Исполнитель
    ADMIN = "admin"        # Администратор

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    completed_tasks = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role = Column(Enum(UserRole), default=UserRole.EXECUTOR)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    boards = relationship("Board", back_populates="owner")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id", back_populates="created_by")
    # Новые связи для заказов и предложений
    created_orders = relationship("Order", foreign_keys="Order.customer_id", back_populates="customer")
    proposals = relationship("Proposal", foreign_keys="Proposal.executor_id", back_populates="executor")
    # Связи для сообщений (добавляются после загрузки всех моделей)
    # sent_messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    # received_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password) 