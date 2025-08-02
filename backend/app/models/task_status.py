from sqlalchemy import Column, Integer, String
from app.database import Base

class TaskStatus(Base):
    __tablename__ = "task_statuses"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    order = Column(Integer, nullable=False)
    