from app.schemas.column import ColumnCreate, ColumnUpdate
from app.models.column import Column
from sqlalchemy.orm import Session
from typing import Optional


class ColumnCRUD:
    def get_by_id(self, db: Session, column_id: int) -> Optional[Column]:
        return db.query(Column).filter(Column.id == column_id).first()
    
    def get_by_board(self, db: Session, board_id: int):
        return (
            db.query(Column)
            .filter(Column.board_id == board_id)
            .order_by(Column.order_index)  # Изменено с order на order_index
            .all()
        )

    def get_by_name_and_board(self, db: Session, title: str, board_id: int) -> Optional[Column]:  # Изменено name на title
        """Получает колонку по названию и ID доски"""
        return db.query(Column).filter(
            Column.title == title,  # Изменено с name на title
            Column.board_id == board_id
        ).first()

    def is_name_unique_in_board(self, db: Session, title: str, board_id: int, exclude_id: int = None) -> bool:  # Изменено name на title
        """Проверяет, уникально ли название колонки в рамках доски"""
        query = db.query(Column).filter(
            Column.title == title,  # Изменено с name на title
            Column.board_id == board_id
        )
        
        if exclude_id:
            query = query.filter(Column.id != exclude_id)
        
        return query.first() is None

    def create(self, db: Session, column: ColumnCreate):
        # Проверяем уникальность названия в рамках доски
        if not self.is_name_unique_in_board(db, column.title, column.board_id):  # Изменено с name на title
            raise ValueError(f"Колонка с названием '{column.title}' уже существует в этой доске")  # Изменено с name на title
        
        db_column = Column(**column.dict())
        db.add(db_column)
        db.commit()
        db.refresh(db_column)
        return db_column
    
    def update(self, db: Session, column_id: int, column_update: ColumnUpdate) -> Optional[Column]:
        db_column = self.get_by_id(db, column_id)
        if not db_column:
            return None
        
        update_data = column_update.dict(exclude_unset=True)
        
        # Если обновляется название, проверяем уникальность
        if 'title' in update_data:  # Изменено с name на title
            if not self.is_name_unique_in_board(db, update_data['title'], db_column.board_id, exclude_id=column_id):  # Изменено с name на title
                raise ValueError(f"Колонка с названием '{update_data['title']}' уже существует в этой доске")  # Изменено с name на title
        
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
    
    def check_owner(self, db: Session, column_id: int, user_id: int) -> bool:
        """Проверяет, является ли пользователь владельцем доски, к которой принадлежит колонка"""
        db_column = self.get_by_id(db, column_id)
        if not db_column:
            return False
        
        # Проверяем владельца доски
        from app.crud.board import board_crud
        return board_crud.check_owner(db, board_id=db_column.board_id, user_id=user_id)
    
    def reorder_columns(self, db: Session, columns: list[dict]):
        for col in columns:
            db_column = db.query(Column).filter(Column.id == col['id']).first()
            if db_column:
                db_column.order_index = col['order_index']  # Изменено с order на order_index
        db.commit()

column_crud = ColumnCRUD()