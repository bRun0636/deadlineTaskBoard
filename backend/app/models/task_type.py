import enum
from sqlalchemy import Column, Integer, String
from app.database import Base

class TaskTypeEnum(enum.Enum):
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    TASK = "task"

class TaskType(Base):
    __tablename__ = "task_types"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    
    # Статические значения для удобства
    PUBLIC = "public"
    PRIVATE = "private"

# Для обратной совместимости
TaskType = TaskTypeEnum 