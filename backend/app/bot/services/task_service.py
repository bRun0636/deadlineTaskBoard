import logging
import json
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.task import Task
from app.models.task_status import TaskStatus
from app.models.task_type import TaskType
from app.models.board import Board
from app.models.column import Column

logger = logging.getLogger(__name__)


class TaskService:
    """
    Сервис для работы с задачами
    """
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    async def get_user_tasks(self, user_id: int) -> List[Task]:
        """
        Получить задачи пользователя
        """
        try:
            stmt = select(Task).where(
                (Task.creator_id == user_id) | (Task.assignee_id == user_id)
            ).order_by(Task.created_at.desc())
            
            result = self.db.execute(stmt)
            tasks = result.scalars().all()
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting tasks for user {user_id}: {e}")
            return []
    
    async def create_task(
        self,
        creator_id: int,
        title: str,
        description: str,
        budget: Optional[float] = None,
        priority: int = 1,
        tags: Optional[List[str]] = None
    ) -> Task:
        """
        Создать новую задачу
        """
        try:
            # Получаем или создаем доску для пользователя
            board = await self._get_or_create_user_board(creator_id)
            
            # Получаем первую колонку (TODO)
            column = await self._get_first_column(board.id)
            
            # Создаем задачу
            task = Task(
                title=title,
                description=description,
                budget=budget,
                priority=priority,
                tags=json.dumps(tags) if tags else None,
                board_id=board.id,
                column_id=column.id,
                creator_id=creator_id,
                status=TaskStatus.TODO,
                type=TaskType.TASK
            )
            
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Task created: {task.id} by user {creator_id}")
            return task
            
        except Exception as e:
            logger.error(f"Error creating task for user {creator_id}: {e}")
            self.db.rollback()
            raise
    
    async def _get_or_create_user_board(self, user_id: int) -> Board:
        """
        Получить или создать доску для пользователя
        """
        try:
            # Ищем существующую доску пользователя
            stmt = select(Board).where(Board.creator_id == user_id)
            result = self.db.execute(stmt)
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
            
            self.db.add(board)
            self.db.commit()
            self.db.refresh(board)
            
            # Создаем стандартные колонки
            await self._create_default_columns(board.id)
            
            return board
            
        except Exception as e:
            logger.error(f"Error getting/creating board for user {user_id}: {e}")
            self.db.rollback()
            raise
    
    async def _create_default_columns(self, board_id: int):
        """
        Создать стандартные колонки для доски
        """
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
                self.db.add(column)
            
            self.db.commit()
            
        except Exception as e:
            logger.error(f"Error creating default columns for board {board_id}: {e}")
            self.db.rollback()
            raise
    
    async def _get_first_column(self, board_id: int) -> Column:
        """
        Получить первую колонку доски
        """
        try:
            stmt = select(Column).where(Column.board_id == board_id).order_by(Column.order_index)
            result = self.db.execute(stmt)
            column = result.scalar_one_or_none()
            
            if not column:
                raise ValueError(f"No columns found for board {board_id}")
            
            return column
            
        except Exception as e:
            logger.error(f"Error getting first column for board {board_id}: {e}")
            raise
    
    async def update_task_status(self, task_id: int, status: TaskStatus) -> bool:
        """
        Обновить статус задачи
        """
        try:
            stmt = select(Task).where(Task.id == task_id)
            result = self.db.execute(stmt)
            task = result.scalar_one_or_none()
            
            if not task:
                return False
            
            task.status = status
            self.db.commit()
            
            logger.info(f"Task {task_id} status updated to {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating task {task_id} status: {e}")
            self.db.rollback()
            return False
    
    async def assign_task(self, task_id: int, assignee_id: int) -> bool:
        """
        Назначить задачу исполнителю
        """
        try:
            stmt = select(Task).where(Task.id == task_id)
            result = self.db.execute(stmt)
            task = result.scalar_one_or_none()
            
            if not task:
                return False
            
            task.assignee_id = assignee_id
            self.db.commit()
            
            logger.info(f"Task {task_id} assigned to user {assignee_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error assigning task {task_id} to user {assignee_id}: {e}")
            self.db.rollback()
            return False
    
    def __del__(self):
        """
        Закрываем соединение с БД
        """
        if hasattr(self, 'db'):
            self.db.close() 