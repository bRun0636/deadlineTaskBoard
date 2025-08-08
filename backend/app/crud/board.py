from sqlalchemy.orm import Session
from app.models.board import Board
from app.schemas.board import BoardCreate, BoardUpdate
from typing import Optional, List

class BoardCRUD:
    def get_by_id(self, db: Session, board_id: int) -> Optional[Board]:
        return db.query(Board).filter(Board.id == board_id).first()
    
    def get_by_id_including_deleted(self, db: Session, board_id: int) -> Optional[Board]:
        """Получить доску по ID, включая удаленные (для админов)"""
        return db.query(Board).filter(Board.id == board_id).first()
    
    def get_by_owner(self, db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> List[Board]:
        return db.query(Board).filter(Board.creator_id == owner_id, Board.is_active == True).offset(skip).limit(limit).all()
    
    def get_public_boards(self, db: Session, skip: int = 0, limit: int = 100) -> List[Board]:
        return db.query(Board).filter(Board.is_public == True, Board.is_active == True).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Board]:
        return db.query(Board).filter(Board.is_active == True).offset(skip).limit(limit).all()
    
    def get_deleted_boards(self, db: Session, skip: int = 0, limit: int = 100) -> List[Board]:
        """Получить все удаленные доски (для админов)"""
        return db.query(Board).filter(Board.is_active == False).offset(skip).limit(limit).all()
    
    def get_all_including_deleted(self, db: Session, skip: int = 0, limit: int = 100) -> List[Board]:
        """Получить все доски, включая удаленные (для админов)"""
        return db.query(Board).offset(skip).limit(limit).all()
    
    def create(self, db: Session, board: BoardCreate, owner_id: int) -> Board:
        db_board = Board(
            title=board.title,
            description=board.description,
            is_public=board.is_public,
            creator_id=owner_id
        )
        db.add(db_board)
        db.commit()
        db.refresh(db_board)
        return db_board
    
    def update(self, db: Session, board_id: int, board_update: BoardUpdate) -> Optional[Board]:
        db_board = self.get_by_id(db, board_id)
        if not db_board:
            return None
        
        update_data = board_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_board, field, value)
        
        db.commit()
        db.refresh(db_board)
        return db_board
    
    def delete(self, db: Session, board_id: int) -> bool:
        db_board = self.get_by_id(db, board_id)
        if not db_board:
            return False
        
        # Мягкое удаление - делаем доску неактивной
        db_board.is_active = False
        db.commit()
        return True
    
    def restore(self, db: Session, board_id: int) -> bool:
        """Восстановить удаленную доску (для админов)"""
        db_board = db.query(Board).filter(Board.id == board_id).first()
        if not db_board:
            return False
        
        # Восстанавливаем доску - делаем активной
        db_board.is_active = True
        db.commit()
        return True
    
    def delete_permanently(self, db: Session, board_id: int) -> bool:
        """Полное удаление доски из базы данных (включая неактивные)"""
        db_board = db.query(Board).filter(Board.id == board_id).first()
        if not db_board:
            return False
        
        # Полное удаление - удаляем из базы данных
        db.delete(db_board)
        db.commit()
        return True
    
    def check_owner(self, db: Session, board_id: int, user_id: int) -> bool:
        board = self.get_by_id(db, board_id)
        return board and board.creator_id == user_id

board_crud = BoardCRUD() 