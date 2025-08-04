import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.database import get_db
from app.models.user import User
from app.models.task import Task
from app.models.order import Order
from app.models.message import Message
from app.models.proposal import Proposal

logger = logging.getLogger(__name__)


class AdminService:
    """
    Сервис для административных функций
    """
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    async def get_all_users(self) -> List[User]:
        """
        Получить всех пользователей
        """
        try:
            stmt = select(User).order_by(User.created_at.desc())
            result = self.db.execute(stmt)
            users = result.scalars().all()
            return list(users)
            
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику системы
        """
        try:
            # Подсчитываем количество пользователей
            users_count = self.db.query(func.count(User.id)).scalar()
            active_users_count = self.db.query(func.count(User.id)).where(User.is_active == True).scalar()
            
            # Подсчитываем количество задач
            tasks_count = self.db.query(func.count(Task.id)).scalar()
            
            # Подсчитываем количество заказов
            orders_count = self.db.query(func.count(Order.id)).scalar()
            
            # Подсчитываем количество сообщений
            messages_count = self.db.query(func.count(Message.id)).scalar()
            
            # Подсчитываем количество предложений
            proposals_count = self.db.query(func.count(Proposal.id)).scalar()
            
            return {
                'total_users': users_count or 0,
                'active_users': active_users_count or 0,
                'total_tasks': tasks_count or 0,
                'total_orders': orders_count or 0,
                'total_messages': messages_count or 0,
                'total_proposals': proposals_count or 0
            }
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {
                'total_users': 0,
                'active_users': 0,
                'total_tasks': 0,
                'total_orders': 0,
                'total_messages': 0,
                'total_proposals': 0
            }
    
    async def get_user_by_id(self, user_id: int) -> User:
        """
        Получить пользователя по ID
        """
        try:
            stmt = select(User).where(User.id == user_id)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()
            return user
            
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user_role(self, user_id: int, role: str) -> bool:
        """
        Обновить роль пользователя
        """
        try:
            stmt = select(User).where(User.id == user_id)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.role = role
                self.db.commit()
                logger.info(f"Updated role for user {user_id} to {role}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating role for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Деактивировать пользователя
        """
        try:
            stmt = select(User).where(User.id == user_id)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.is_active = False
                self.db.commit()
                logger.info(f"Deactivated user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            self.db.rollback()
            return False
    
    def __del__(self):
        """
        Закрываем соединение с БД
        """
        if hasattr(self, 'db'):
            self.db.close() 