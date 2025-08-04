import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.order import Order
from app.models.user import User

logger = logging.getLogger(__name__)


class OrderService:
    """
    Сервис для работы с заказами
    """
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """
        Получить заказы пользователя
        """
        try:
            stmt = select(Order).where(
                (Order.creator_id == user_id) | (Order.assigned_executor_id == user_id)
            ).order_by(Order.created_at.desc())
            
            result = self.db.execute(stmt)
            orders = result.scalars().all()
            return list(orders)
            
        except Exception as e:
            logger.error(f"Error getting orders for user {user_id}: {e}")
            return []
    
    async def get_available_orders(self) -> List[Order]:
        """
        Получить доступные заказы (статус 'open')
        """
        try:
            stmt = select(Order).where(Order.status == 'open').order_by(Order.created_at.desc())
            result = self.db.execute(stmt)
            orders = result.scalars().all()
            return list(orders)
            
        except Exception as e:
            logger.error(f"Error getting available orders: {e}")
            return []
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """
        Получить заказ по ID
        """
        try:
            stmt = select(Order).where(Order.id == order_id)
            result = self.db.execute(stmt)
            order = result.scalar_one_or_none()
            return order
            
        except Exception as e:
            logger.error(f"Error getting order {order_id}: {e}")
            return None
    
    async def create_order(self, order_data: dict) -> Optional[Order]:
        """
        Создать новый заказ
        """
        try:
            order = Order(**order_data)
            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)
            
            logger.info(f"Created order {order.id} by user {order.creator_id}")
            return order
            
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            self.db.rollback()
            return None
    
    async def update_order(self, order_id: int, order_data: dict) -> bool:
        """
        Обновить заказ
        """
        try:
            stmt = select(Order).where(Order.id == order_id)
            result = self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if order:
                for key, value in order_data.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
                
                self.db.commit()
                logger.info(f"Updated order {order_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {e}")
            self.db.rollback()
            return False
    
    async def delete_order(self, order_id: int) -> bool:
        """
        Удалить заказ
        """
        try:
            stmt = select(Order).where(Order.id == order_id)
            result = self.db.execute(stmt)
            order = result.scalar_one_or_none()
            
            if order:
                self.db.delete(order)
                self.db.commit()
                logger.info(f"Deleted order {order_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting order {order_id}: {e}")
            self.db.rollback()
            return False
    
    def __del__(self):
        """
        Закрываем соединение с БД
        """
        if hasattr(self, 'db'):
            self.db.close() 