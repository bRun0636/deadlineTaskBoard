from sqlalchemy.orm import Session
from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate
from typing import Optional, List

class TaskCRUD:
    def get_by_id(self, db: Session, task_id: int) -> Optional[Task]:
        return db.query(Task).filter(Task.id == task_id).first()
    
    def get_by_board(self, db: Session, board_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task).filter(Task.board_id == board_id).offset(skip).limit(limit).all()
    
    def get_by_status(self, db: Session, board_id: int, column_id: int) -> List[Task]:
        return db.query(Task).filter(Task.board_id == board_id, Task.column_id == column_id).all()
    
    def get_by_assigned_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task).filter(Task.assignee_id == user_id).offset(skip).limit(limit).all()
    
    def get_by_creator(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task).filter(Task.creator_id == user_id).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Task]:
        return db.query(Task).offset(skip).limit(limit).all()
    
    def create(self, db: Session, task: TaskCreate, created_by_id: int) -> Task:
        # Конвертируем tags из списка в строку
        tags_str = ','.join(task.tags) if task.tags else None
        
        db_task = Task(
            title=task.title,
            description=task.description,
            priority=task.priority,
            budget=task.budget,
            due_date=task.due_date,
            tags=tags_str,
            board_id=task.board_id,
            assignee_id=task.assigned_to_id,
            creator_id=created_by_id,
            column_id=task.column_id,
            parent_id=task.parent_id
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def update(self, db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
        db_task = self.get_by_id(db, task_id)
        if not db_task:
            return None
        
        update_data = task_update.dict(exclude_unset=True)
        
        # Конвертируем tags из списка в строку, если они есть
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = ','.join(update_data['tags'])
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def update_status(self, db: Session, task_id: int, column_id: int) -> Optional[Task]:
        db_task = self.get_by_id(db, task_id)
        if not db_task:
            return None
        
        db_task.column_id = column_id
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def delete(self, db: Session, task_id: int) -> bool:
        db_task = self.get_by_id(db, task_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    def get_tasks_by_board_and_columns(self, db: Session, board_id: int) -> dict:
        """Получить задачи, сгруппированные по колонкам для канбан-доски"""
        tasks = self.get_by_board(db, board_id)
        grouped_tasks = {}
        
        for task in tasks:
            if task.column_id:
                if task.column_id not in grouped_tasks:
                    grouped_tasks[task.column_id] = []
                grouped_tasks[task.column_id].append(task)
        
        return grouped_tasks

task_crud = TaskCRUD() 