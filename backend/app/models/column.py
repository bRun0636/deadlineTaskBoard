from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base

class Column(Base):
    __tablename__ = "columns"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)  # Изменено с name на title
    order_index = Column(Integer, index=True)  # Изменено с order на order_index

    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)

    # Составной уникальный индекс: имя колонки должно быть уникальным в рамках одной доски
    __table_args__ = (
        UniqueConstraint('title', 'board_id', name='uq_column_title_per_board'),  # Изменено с name на title
    )

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column")