from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.column import ColumnCreate, ColumnUpdate, ColumnResponse, ColumnReorder
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.crud.column import column_crud

router = APIRouter(prefix="/columns", tags=["columns"])

@router.post("/", response_model=ColumnCreate)
def create_column(
    column: ColumnCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user)
):
    """Создать новую колонку"""
    try:
        result = column_crud.create(db=db, column=column)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{column_id}", response_model=ColumnResponse)
def update_column(
    column_id: int,
    column_update: ColumnUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить колонку"""
    # Проверяем, является ли пользователь владельцем колонки
    if not column_crud.check_owner(db, column_id=column_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    try:
        column = column_crud.update(db, column_id=column_id, column_update=column_update)
        if column is None:
            raise HTTPException(status_code=404, detail="Column not found")
        return column
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{column_id}")
def delete_column(
    column_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить колонку"""
    # Проверяем, является ли пользователь владельцем колонки
    if not column_crud.check_owner(db, column_id=column_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    column_crud.delete(db, column_id=column_id)
    return {"message": "Column deleted successfully"}

@router.get("/board/{board_id}", response_model=List[ColumnResponse])
def read_board_columns(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить колонки доски"""
    columns = column_crud.get_by_board(db=db, board_id=board_id)
    return columns


@router.patch("/reorder", status_code=200)
def reorder_columns(
    reordered_columns: List[ColumnReorder],
    db: Session = Depends(get_db),
    _: User = Depends(get_current_active_user)
):
    """Обновить порядок колонок"""
    column_crud.reorder_columns(db=db, columns=[col.dict() for col in reordered_columns])
    return {"message": "Column order updated"}