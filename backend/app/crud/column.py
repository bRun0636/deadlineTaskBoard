from sqlalchemy.orm import Session
from app.models.column import Column
from app.schemas.column import ColumnCreate, ColumnUpdate
from typing import Optional, List

class ColumnCRUD:
    def get_by_id(self, db: Session, column_id: int) -> Optional[Column]:
        return db.query(Column).filter(Column.id == column_id).first()
    
    def get_by_board(self, db: Session, board_id: int, skip: int = 0, limit: int = 100) -> List[Column]:
        return db.query(Column).filter(Column.board_id == board_id).order_by(Column.order_index).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Column]:
        return db.query(Column).order_by(Column.order_index).offset(skip).limit(limit).all()
    
    def create(self, db: Session, column: ColumnCreate, board_id: int) -> Column:
        # Получаем максимальный order_index для доски
        max_order = db.query(Column).filter(Column.board_id == board_id).with_entities(db.func.max(Column.order_index)).scalar() or 0
        
        db_column = Column(
            title=column.title,
            order_index=max_order + 1,
            board_id=board_id
        )
        db.add(db_column)
        db.commit()
        db.refresh(db_column)
        return db_column
    
    def update(self, db: Session, column_id: int, column_update: ColumnUpdate) -> Optional[Column]:
        db_column = self.get_by_id(db, column_id)
        if not db_column:
            return None
        
        update_data = column_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_column, field, value)
        
        db.commit()
        db.refresh(db_column)
        return db_column
    
    def delete(self, db: Session, column_id: int) -> bool:
        db_column = self.get_by_id(db, column_id)
        if not db_column:
            return False
        
        db.delete(db_column)
        db.commit()
        return True
    
    def reorder(self, db: Session, columns_data: List[dict]) -> bool:
        """Переупорядочивание колонок"""
        try:
            for col_data in columns_data:
                column_id = col_data.get('id')
                new_order = col_data.get('order_index')
                if column_id and new_order is not None:
                    column = self.get_by_id(db, column_id)
                    if column:
                        column.order_index = new_order
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    def check_board_owner(self, db: Session, column_id: int, user_id: int) -> bool:
        """Проверка, является ли пользователь владельцем доски колонки"""
        column = self.get_by_id(db, column_id)
        if not column:
            return False
        
        from app.models.board import Board
        board = db.query(Board).filter(Board.id == column.board_id).first()
        return board and board.creator_id == user_id

column_crud = ColumnCRUD()