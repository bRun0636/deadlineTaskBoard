import logging
import json
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.database import get_db
from app.models.task import Task
from app.models.task_status import TaskStatus
from app.models.task_type import TaskType, TaskTypeEnum
from app.models.board import Board
from app.models.column import Column
from app.crud.task import task_crud
from app.models.user import User

logger = logging.getLogger(__name__)


class TaskService:
    """
    Сервис для работы с задачами
    """
    
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        """Получить подключение к базе данных"""
        return next(get_db())
    
    async def get_user_tasks(self, user_id: int) -> List[Task]:
        """
        Получить задачи пользователя
        """
        try:
            db = self._get_db()
            try:
                # Загружаем задачи с предзагруженными связанными данными
                stmt = select(Task).options(
                    joinedload(Task.creator),
                    joinedload(Task.assignee),
                    joinedload(Task.board)
                ).where(Task.creator_id == user_id)
                result = db.execute(stmt)
                tasks = result.scalars().unique().all()
                return tasks
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting user tasks: {e}")
            return []
    
    async def get_all_tasks(self) -> List[Task]:
        """Получить все задачи"""
        try:
            db = self._get_db()
            try:
                # Загружаем задачи с предзагруженными связанными данными
                stmt = select(Task).options(
                    joinedload(Task.creator),
                    joinedload(Task.assignee),
                    joinedload(Task.board)
                )
                result = db.execute(stmt)
                tasks = result.scalars().unique().all()
                return tasks
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting all tasks: {e}")
            return []
    
    async def get_task_statistics(self, user_id: int = None) -> Dict:
        """Получить статистику задач (общую или пользователя)"""
        try:
            db = self._get_db()
            try:
                if user_id:
                    # Статистика для конкретного пользователя
                    tasks = task_crud.get_by_creator(db, user_id=user_id)
                else:
                    # Общая статистика всех задач
                    tasks = task_crud.get_multi(db)
                
                stats = {
                    'total': len(tasks),
                                    'pending': len([t for t in tasks if t.status == TaskStatus.TODO.value]),
                'in_progress': len([t for t in tasks if t.status == TaskStatus.IN_PROGRESS.value]),
                'completed': len([t for t in tasks if t.status == TaskStatus.DONE.value]),
                'cancelled': len([t for t in tasks if t.status == TaskStatus.CANCELLED.value]),
                    'total_budget': sum(t.budget or 0 for t in tasks)
                }
                
                # Статистика по приоритетам
                priority_stats = {}
                for task in tasks:
                    priority = task.priority or 1
                    priority_stats[priority] = priority_stats.get(priority, 0) + 1
                stats['by_priority'] = priority_stats
                
                # Продуктивность (только для завершенных задач)
                completed_tasks = [t for t in tasks if t.status == TaskStatus.DONE.value]
                if completed_tasks:
                    # Среднее время выполнения
                    completion_times = []
                    for task in completed_tasks:
                        if task.created_at and task.updated_at:
                            completion_time = (task.updated_at - task.created_at).days
                            completion_times.append(completion_time)
                    
                    if completion_times:
                        stats['productivity'] = {
                            'avg_completion_time': sum(completion_times) / len(completion_times),
                            'on_time_percentage': 87.0,  # Примерное значение
                            'avg_rating': 4.6  # Примерное значение
                        }
                
                return stats
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting task statistics: {e}")
            return {
                'total': 0,
                'pending': 0,
                'in_progress': 0,
                'completed': 0,
                'cancelled': 0,
                'total_budget': 0,
                'by_priority': {},
                'productivity': {}
            }
    
    async def create_task(self, task_data: Dict, user_id: int) -> Optional[Task]:
        """Создать новую задачу"""
        try:
            from app.schemas.task import TaskCreate
            task_create = TaskCreate(**task_data)
            db = self._get_db()
            try:
                return task_crud.create(db, task=task_create, created_by_id=user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    async def update_task(self, task_id: int, task_data: Dict) -> Optional[Task]:
        """Обновить задачу"""
        try:
            from app.schemas.task import TaskUpdate
            task_update = TaskUpdate(**task_data)
            db = self._get_db()
            try:
                return task_crud.update(db, task_id=task_id, task_update=task_update)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return None
    
    async def delete_task(self, task_id: int) -> bool:
        """Удалить задачу"""
        try:
            db = self._get_db()
            try:
                return task_crud.delete(db, task_id=task_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return False
    
    async def _get_or_create_user_board(self, user_id: int) -> Board:
        """
        Получить или создать доску для пользователя
        """
        try:
            db = self._get_db()
            try:
                # Ищем существующую доску пользователя
                stmt = select(Board).where(Board.creator_id == user_id)
                result = db.execute(stmt)
                board = result.scalar_one_or_none()
                
                if board:
                    return board
                
                # Создаем новую доску
                board = Board(
                    title="Мои задачи",
                    description="Персональная доска задач",
                    creator_id=user_id,
                    is_public=False
                )
                
                db.add(board)
                db.commit()
                db.refresh(board)
                
                # Создаем стандартные колонки
                await self._create_default_columns(board.id)
                
                return board
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting/creating board for user {user_id}: {e}")
            raise
    
    async def _create_default_columns(self, board_id: int):
        """
        Создать стандартные колонки для доски
        """
        try:
            db = self._get_db()
            try:
                columns_data = [
                    {"title": "К выполнению", "order_index": 1},
                    {"title": "В работе", "order_index": 2},
                    {"title": "Готово", "order_index": 3}
                ]
                
                for col_data in columns_data:
                    column = Column(
                        title=col_data["title"],
                        order_index=col_data["order_index"],
                        board_id=board_id
                    )
                    db.add(column)
                
                db.commit()
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error creating default columns for board {board_id}: {e}")
            raise
    
    async def _get_first_column(self, board_id: int) -> Column:
        """
        Получить первую колонку доски
        """
        try:
            db = self._get_db()
            try:
                stmt = select(Column).where(Column.board_id == board_id).order_by(Column.order_index)
                result = db.execute(stmt)
                column = result.scalar_one_or_none()
                
                if not column:
                    raise ValueError(f"No columns found for board {board_id}")
                
                return column
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting first column for board {board_id}: {e}")
            raise
    
    async def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """
        Обновить статус задачи
        """
        try:
            db = self._get_db()
            try:
                stmt = select(Task).where(Task.id == task_id)
                result = db.execute(stmt)
                task = result.scalar_one_or_none()
                
                if task:
                    task.status = status
                    db.commit()
                    logger.info(f"Updated task {task_id} status to {status}")
                    return True
                
                return False
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error updating task status: {e}")
            return False
    
    async def assign_task(self, task_id: int, assignee_id: int) -> bool:
        """
        Назначить задачу исполнителю
        """
        try:
            db = self._get_db()
            try:
                stmt = select(Task).where(Task.id == task_id)
                result = db.execute(stmt)
                task = result.scalar_one_or_none()
                
                if task:
                    task.assignee_id = assignee_id
                    task.status = TaskStatus.IN_PROGRESS.value
                    db.commit()
                    logger.info(f"Assigned task {task_id} to user {assignee_id}")
                    return True
                
                return False
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error assigning task: {e}")
            return False 