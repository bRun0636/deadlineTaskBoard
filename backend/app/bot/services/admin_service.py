import logging
from typing import List, Dict, Any
from sqlalchemy.orm import Session, joinedload
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
        pass
    
    def _get_db(self) -> Session:
        """Получить подключение к базе данных"""
        return next(get_db())
    
    async def get_all_users(self) -> List[User]:
        """
        Получить всех пользователей
        """
        try:
            db = self._get_db()
            try:
                stmt = select(User).order_by(User.created_at.desc())
                result = db.execute(stmt)
                users = result.scalars().all()
                return list(users)
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []
    
    async def get_system_statistics(self) -> Dict[str, Any]:
        """
        Получить статистику системы
        """
        try:
            db = self._get_db()
            try:
                # Подсчитываем количество пользователей
                users_count = db.query(func.count(User.id)).scalar()
                active_users_count = db.query(func.count(User.id)).where(User.is_active == True).scalar()
                
                # Подсчитываем количество задач
                tasks_count = db.query(func.count(Task.id)).scalar()
                
                # Подсчитываем количество заказов
                orders_count = db.query(func.count(Order.id)).scalar()
                
                # Подсчитываем количество сообщений
                messages_count = db.query(func.count(Message.id)).scalar()
                
                # Подсчитываем количество предложений
                proposals_count = db.query(func.count(Proposal.id)).scalar()
                
                return {
                    'total_users': users_count or 0,
                    'active_users': active_users_count or 0,
                    'total_tasks': tasks_count or 0,
                    'total_orders': orders_count or 0,
                    'total_messages': messages_count or 0,
                    'total_proposals': proposals_count or 0
                }
                
            finally:
                db.close()
                
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
            db = self._get_db()
            try:
                stmt = select(User).where(User.id == user_id)
                result = db.execute(stmt)
                user = result.scalar_one_or_none()
                return user
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    async def update_user_role(self, user_id: int, role: str) -> bool:
        """
        Обновить роль пользователя
        """
        try:
            db = self._get_db()
            try:
                stmt = select(User).where(User.id == user_id)
                result = db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    user.role = role
                    db.commit()
                    logger.info(f"Updated role for user {user_id} to {role}")
                    return True
                
                return False
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error updating role for user {user_id}: {e}")
            return False
    
    async def deactivate_user(self, user_id: int) -> bool:
        """
        Деактивировать пользователя
        """
        try:
            db = self._get_db()
            try:
                stmt = select(User).where(User.id == user_id)
                result = db.execute(stmt)
                user = result.scalar_one_or_none()
                
                if user:
                    user.is_active = False
                    db.commit()
                    logger.info(f"Deactivated user {user_id}")
                    return True
                
                return False
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error deactivating user {user_id}: {e}")
            return False 