from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from app.models.task_status import TaskStatusEnum
from app.models.task_type import TaskTypeEnum

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=TaskStatusEnum.TODO.value)
    type = Column(String(20), default=TaskTypeEnum.TASK.value)
    priority = Column(Integer, default=1)
    budget = Column(Float, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    tags = Column(String, nullable=True)
    
    # Foreign Keys
    board_id = Column(Integer, ForeignKey("boards.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)
    column_id = Column(Integer, ForeignKey("columns.id", ondelete="CASCADE"))

    # Связь со статусом через колонку `column_id`
    column = relationship("Column", back_populates="tasks")
    # Остальные связи
    board = relationship("Board", back_populates="tasks")
    assigned_to = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    created_by = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks", cascade="all, delete") 

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())