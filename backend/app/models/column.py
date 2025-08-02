from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Column(Base):
    __tablename__ = "columns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    order = Column(Integer, index=True)

    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)

    # Составной уникальный индекс: имя колонки должно быть уникальным в рамках одной доски
    __table_args__ = (
        UniqueConstraint('name', 'board_id', name='uq_column_name_per_board'),
    )

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column")