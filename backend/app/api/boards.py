from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.board import board_crud
from app.crud.task import task_crud
from app.schemas.board import BoardCreate, BoardUpdate, BoardResponse, BoardWithTasks
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.crud.column import column_crud

router = APIRouter(prefix="/boards", tags=["boards"])

@router.post("/", response_model=BoardResponse)
def create_board(
    board: BoardCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новую доску"""
    result = board_crud.create(db=db, board=board, owner_id=current_user.id)
    return result

@router.get("/", response_model=List[BoardResponse])
def read_boards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить доски текущего пользователя"""
    boards = board_crud.get_by_owner(db, owner_id=current_user.id, skip=skip, limit=limit)
    return boards

@router.get("/public", response_model=List[BoardResponse])
def read_public_boards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Получить публичные доски"""
    return board_crud.get_public_boards(db, skip=skip, limit=limit)

@router.get("/{board_id}", response_model=BoardWithTasks)
def read_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить доску по ID"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Requesting board with ID: {board_id}")
    board = board_crud.get_by_id(db, board_id=board_id)
    
    if board is None:
        logger.warning(f"Board {board_id} not found")
        raise HTTPException(status_code=404, detail="Board not found")
    
    logger.info(f"Board {board_id} found: {board.title}")
    
    # Проверяем права доступа
    if not board.is_public and board.creator_id != current_user.id:
        logger.warning(f"User {current_user.id} has no access to board {board_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    board.columns = column_crud.get_by_board(db=db, board_id=board_id)
    board.tasks = task_crud.get_by_board(db=db, board_id=board_id)
    logger.info(f"Returning board {board_id} with {len(board.columns)} columns and {len(board.tasks)} tasks")
    logger.info(f"Board data: id={board.id}, title='{board.title}'")

    return board



@router.put("/{board_id}", response_model=BoardResponse)
def update_board(
    board_id: int,
    board_update: BoardUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить доску"""
    # Проверяем, является ли пользователь владельцем доски
    if not board_crud.check_owner(db, board_id=board_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    board = board_crud.update(db, board_id=board_id, board_update=board_update)
    if board is None:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.delete("/{board_id}")
def delete_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить доску"""
    # Проверяем, является ли пользователь владельцем доски
    if not board_crud.check_owner(db, board_id=board_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = board_crud.delete(db, board_id=board_id)
    if not success:
        raise HTTPException(status_code=404, detail="Board not found")
    return {"message": "Board deleted successfully"} 