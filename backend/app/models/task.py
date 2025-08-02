from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="medium")
    budget = Column(Float, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(ARRAY(String), default=[])
    rating = Column(Float, nullable=True)
    
    # Foreign Keys
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    column_id = Column(Integer, ForeignKey("columns.id", ondelete="CASCADE"))

    # Связь со статусом через колонку `column_id`
    column = relationship("Column", back_populates="tasks")
    # Остальные связи
    board = relationship("Board", back_populates="tasks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks", cascade="all, delete") 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())