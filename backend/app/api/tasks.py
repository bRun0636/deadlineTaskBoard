from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict
from app.database import get_db
from app.crud.task import task_crud
from app.crud.board import board_crud
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskStatusUpdate, TaskWithRelations
from app.auth.dependencies import get_current_active_user
from app.models.user import User
from app.models.task import Task

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskCreate)
def create_task(
    task: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новую задачу"""
    # Проверяем, существует ли доска и есть ли права доступа
    board = board_crud.get_by_id(db, board_id=task.board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return task_crud.create(db=db, task=task, created_by_id=current_user.id)

@router.get("/", response_model=List[TaskResponse])
def read_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить все задачи (для суперпользователей)"""
    tasks = task_crud.get_all(db, skip=skip, limit=limit)
    return tasks

@router.get("/my", response_model=List[TaskResponse])
def read_my_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить задачи, созданные текущим пользователем"""
    tasks = task_crud.get_by_creator(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.get("/assigned", response_model=List[TaskResponse])
def read_assigned_tasks(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить задачи, назначенные текущему пользователю"""
    tasks = task_crud.get_by_assigned_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return tasks

@router.get("/board/{board_id}", response_model=List[TaskResponse])
def read_board_tasks(
    board_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить задачи конкретной доски"""
    # Проверяем права доступа к доске
    board = board_crud.get_by_id(db, board_id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    tasks = task_crud.get_by_board(db, board_id=board_id, skip=skip, limit=limit)
    return tasks

@router.get("/board/{board_id}/kanban", response_model=Dict[str, List[TaskResponse]])
def read_board_kanban(
    board_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить задачи доски, сгруппированные по статусам для канбан-доски"""
    # Проверяем права доступа к доске
    board = board_crud.get_by_id(db, board_id=board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    grouped_tasks = task_crud.get_tasks_by_board_and_columns(db, board_id=board_id)
    return grouped_tasks

@router.get("/{task_id}", response_model=TaskWithRelations)
def read_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить задачу по ID"""
    task = task_crud.get_by_id(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем права доступа к доске
    board = board_crud.get_by_id(db, board_id=task.board_id)
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return task

@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    task_update: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить задачу"""
    # Проверяем, существует ли задача
    task = task_crud.get_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем права доступа к доске
    board = board_crud.get_by_id(db, board_id=task.board_id)
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_task = task_crud.update(db, task_id=task_id, task_update=task_update)
    return updated_task

@router.patch("/{task_id}/status", response_model=TaskStatusUpdate)
def update_task_status(
    task_id: int,
    column_id: TaskStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить статус задачи"""
    # Проверяем, существует ли задача
    task = task_crud.get_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем права доступа к доске
    board = board_crud.get_by_id(db, board_id=task.board_id)
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    updated_task = task_crud.update_status(db, task_id=task_id, column_id=column_id.column_id)
    return updated_task

@router.get("/stats/user", response_model=dict)
def get_user_task_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить статистику задач пользователя"""
    # Получаем все активные доски пользователя
    user_boards = board_crud.get_by_owner(db, owner_id=current_user.id)
    
    # Подсчитываем задачи на досках пользователя
    total_tasks = 0
    if user_boards:
        board_ids = [board.id for board in user_boards]
        total_tasks = db.query(Task).filter(Task.board_id.in_(board_ids)).count()
    
    # Подсчитываем задачи, созданные пользователем
    created_tasks = task_crud.get_by_creator(db, user_id=current_user.id, skip=0, limit=1000)
    
    # Подсчитываем задачи, назначенные пользователю
    assigned_tasks = task_crud.get_by_assigned_user(db, user_id=current_user.id, skip=0, limit=1000)
    
    return {
        "total_tasks": total_tasks,
        "created_tasks": len(created_tasks),
        "assigned_tasks": len(assigned_tasks)
    }

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить задачу"""
    # Проверяем, существует ли задача
    task = task_crud.get_by_id(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем права доступа к доске
    board = board_crud.get_by_id(db, board_id=task.board_id)
    if not board.is_public and board.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = task_crud.delete(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"} 
