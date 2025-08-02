from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.user import user_crud
from app.crud.board import board_crud
from app.crud.task import task_crud
from app.schemas.user import UserResponse, UserAdminUpdate, SystemStats
from app.schemas.board import BoardResponse
from app.auth.dependencies import get_current_superuser
from app.models.user import User
from app.models.board import Board
from app.models.task import Task

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/stats", response_model=SystemStats)
def get_system_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить статистику системы"""
    import logging
    logger = logging.getLogger(__name__)
    
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    total_boards = db.query(Board).count()
    active_boards = db.query(Board).filter(Board.is_active == True).count()
    total_tasks = db.query(Task).count()
    completed_tasks = db.query(Task).filter(Task.column_id.isnot(None)).count()
    superusers = db.query(User).filter(User.is_superuser == True).count()
    
    stats = SystemStats(
        total_users=total_users,
        active_users=active_users,
        total_boards=total_boards,
        active_boards=active_boards,
        total_tasks=total_tasks,
        completed_tasks=completed_tasks,
        superusers=superusers
    )
    
    logger.info(f"System stats: {stats}")
    return stats

@router.get("/users", response_model=List[UserResponse])
def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить всех пользователей"""
    users = user_crud.get_all(db, skip=skip, limit=limit)
    return users

@router.get("/users/active", response_model=List[UserResponse])
def get_active_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить активных пользователей"""
    users = user_crud.get_active_users(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}", response_model=UserResponse)
def update_user_admin(
    user_id: int,
    user_update: UserAdminUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Обновить пользователя (админ)"""
    # Нельзя изменить самого себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot modify your own admin status"
        )
    
    update_data = user_update.dict(exclude_unset=True)
    user = user_crud.update_admin(db, user_id=user_id, user_update=update_data)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/boards", response_model=List[BoardResponse])
def get_all_boards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить все активные доски"""
    boards = board_crud.get_all(db, skip=skip, limit=limit)
    return boards

@router.get("/boards/deleted", response_model=List[BoardResponse])
def get_deleted_boards(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить все удаленные доски"""
    boards = board_crud.get_deleted_boards(db, skip=skip, limit=limit)
    return boards

@router.get("/boards/all", response_model=List[BoardResponse])
def get_all_boards_including_deleted(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить все доски, включая удаленные"""
    boards = board_crud.get_all_including_deleted(db, skip=skip, limit=limit)
    return boards

@router.get("/boards/{board_id}", response_model=BoardResponse)
def get_board_by_id(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Получить доску по ID, включая удаленные"""
    board = board_crud.get_by_id_including_deleted(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.put("/boards/{board_id}/restore")
def restore_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Восстановить удаленную доску"""
    success = board_crud.restore(db, board_id)
    if not success:
        raise HTTPException(status_code=404, detail="Deleted board not found")
    
    return {"message": "Board restored successfully"}

@router.put("/boards/{board_id}/activate")
def activate_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Активировать доску"""
    board = board_crud.get_by_id(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    board.is_active = True
    db.commit()
    return {"message": "Board activated successfully"}

@router.put("/boards/{board_id}/deactivate")
def deactivate_board(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Деактивировать доску"""
    board = board_crud.get_by_id(db, board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    board.is_active = False
    db.commit()
    return {"message": "Board deactivated successfully"}

@router.delete("/boards/{board_id}")
def delete_board_permanently(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Полностью удалить доску (только для суперпользователей)"""
    # Ищем доску без фильтра по активности (админ может удалить любую доску)
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    success = board_crud.delete_permanently(db, board_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete board")
    
    return {"message": "Board permanently deleted"} 