import logging
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from app.database import get_db
from app.models.message import Message
from app.models.order import Order
from app.models.user import User

logger = logging.getLogger(__name__)


class ChatService:
    """
    Сервис для работы с чатами и сообщениями
    """
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    async def get_user_chats(self, user_id: int) -> List[Order]:
        """
        Получить чаты пользователя (заказы с сообщениями)
        """
        try:
            # Получаем заказы пользователя, где есть сообщения
            stmt = select(Order).where(
                (Order.creator_id == user_id) | (Order.assigned_executor_id == user_id)
            ).order_by(Order.updated_at.desc())
            
            result = self.db.execute(stmt)
            orders = result.scalars().all()
            
            # Фильтруем только те заказы, где есть сообщения
            chats = []
            for order in orders:
                messages = await self.get_order_messages(order.id)
                if messages:
                    # Добавляем информацию о последнем сообщении
                    order.last_message_time = messages[-1].created_at
                    order.message_count = len(messages)
                    chats.append(order)
            
            return chats
            
        except Exception as e:
            logger.error(f"Error getting chats for user {user_id}: {e}")
            return []
    
    async def get_order_messages(self, order_id: int) -> List[Message]:
        """
        Получить сообщения для заказа
        """
        try:
            stmt = select(Message).where(Message.order_id == order_id).order_by(Message.created_at.asc())
            result = self.db.execute(stmt)
            messages = result.scalars().all()
            return list(messages)
            
        except Exception as e:
            logger.error(f"Error getting messages for order {order_id}: {e}")
            return []
    
    async def send_message(self, user_id: int, order_id: int, message_text: str) -> bool:
        """
        Отправить сообщение в заказ
        """
        try:
            # Проверяем, что заказ существует и пользователь имеет к нему доступ
            order = await self.get_order_by_id(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return False
            
            # Проверяем, что пользователь является участником заказа
            if order.creator_id != user_id and order.assigned_executor_id != user_id:
                logger.error(f"User {user_id} has no access to order {order_id}")
                return False
            
            # Проверяем, что заказ в статусе, где можно отправлять сообщения
            if order.status not in ['in_progress', 'completed']:
                logger.error(f"Order {order_id} is not in progress or completed")
                return False
            
            # Создаем сообщение
            message = Message(
                order_id=order_id,
                sender_id=user_id,
                receiver_id=order.creator_id if user_id == order.assigned_executor_id else order.assigned_executor_id,
                content=message_text,
                created_at=datetime.utcnow()
            )
            
            self.db.add(message)
            self.db.commit()
            self.db.refresh(message)
            
            logger.info(f"Message sent to order {order_id} by user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending message to order {order_id}: {e}")
            self.db.rollback()
            return False
    
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
    
    def __del__(self):
        """
        Закрываем соединение с БД
        """
        if hasattr(self, 'db'):
            self.db.close() 