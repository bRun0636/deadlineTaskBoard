import enum
from sqlalchemy import Column, Integer, String
from app.database import Base

class TaskStatusEnum(enum.Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"
    CANCELLED = "cancelled"

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)

# Для обратной совместимости
# TaskStatus = TaskStatusEnum
    