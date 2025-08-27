import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, desc

from app.database import get_db
from app.models.message import Message
from app.models.user import User
from app.models.order import Order
from app.models.proposal import Proposal

logger = logging.getLogger(__name__)


class ChatService:
    """
    Сервис для работы с чатами и сообщениями
    """
    
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        """Получить подключение к базе данных"""
        return next(get_db())
    
    async def get_chat_messages(self, order_id: int, limit: int = 50) -> List[Message]:
        """
        Получить сообщения чата для заказа
        """
        try:
            db = self._get_db()
            try:
                # Загружаем сообщения с предзагруженными связанными данными
                stmt = select(Message).options(
                    joinedload(Message.sender),
                    joinedload(Message.order)
                ).where(
                    Message.order_id == order_id
                ).order_by(desc(Message.created_at)).limit(limit)
                
                result = db.execute(stmt)
                messages = result.scalars().unique().all()
                return messages
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting chat messages for order {order_id}: {e}")
            return []
    
    async def send_message(self, order_id: int, sender_id: int, content: str) -> Optional[Message]:
        """
        Отправить сообщение в чат
        """
        try:
            db = self._get_db()
            try:
                message = Message(
                    content=content,
                    sender_id=sender_id,
                    order_id=order_id
                )
                
                db.add(message)
                db.commit()
                db.refresh(message)
                
                logger.info(f"Message sent in order {order_id} by user {sender_id}")
                return message
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return None
    
    async def get_user_chats(self, user_id: int) -> List[Dict]:
        """
        Получить список чатов пользователя
        """
        try:
            db = self._get_db()
            try:
                # Получаем заказы, где пользователь является участником
                stmt = select(Order).options(
                    joinedload(Order.creator),
                    joinedload(Order.proposals).joinedload(Proposal.executor)
                ).where(
                    (Order.creator_id == user_id) | 
                    (Order.proposals.any(Proposal.user_id == user_id))
                )
                
                result = db.execute(stmt)
                orders = result.scalars().unique().all()
                
                chats = []
                for order in orders:
                    # Получаем последнее сообщение для каждого заказа
                    last_message_stmt = select(Message).where(
                        Message.order_id == order.id
                    ).order_by(desc(Message.created_at)).limit(1)
                    
                    last_message_result = db.execute(last_message_stmt)
                    last_message = last_message_result.scalar_one_or_none()
                    
                    chats.append({
                        'order_id': order.id,
                        'order_title': order.title,
                        'last_message': last_message.content if last_message else None,
                        'last_message_time': last_message.created_at if last_message else None,
                        'participants': [order.creator.display_name] + [
                            p.executor.display_name for p in order.proposals if p.user_id != user_id
                        ]
                    })
                
                return chats
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting user chats: {e}")
            return []
    
    async def mark_messages_as_read(self, order_id: int, user_id: int) -> bool:
        """
        Отметить сообщения как прочитанные
        """
        try:
            db = self._get_db()
            try:
                # Обновляем статус всех непрочитанных сообщений
                stmt = select(Message).where(
                    Message.order_id == order_id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
                
                result = db.execute(stmt)
                messages = result.scalars().all()
                
                for message in messages:
                    message.is_read = True
                
                db.commit()
                logger.info(f"Marked messages as read in order {order_id} for user {user_id}")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")
            return False
    
    async def get_new_messages(self, user_id: int) -> List[Message]:
        """
        Получить новые сообщения для пользователя
        """
        try:
            db = self._get_db()
            try:
                # Получаем заказы пользователя
                user_orders_stmt = select(Order.id).where(
                    (Order.creator_id == user_id) | 
                    (Order.proposals.any(Proposal.user_id == user_id))
                )
                
                user_orders_result = db.execute(user_orders_stmt)
                user_order_ids = [order.id for order in user_orders_result.scalars().all()]
                
                if not user_order_ids:
                    return []
                
                # Получаем непрочитанные сообщения в заказах пользователя
                stmt = select(Message).options(
                    joinedload(Message.sender),
                    joinedload(Message.order)
                ).where(
                    Message.order_id.in_(user_order_ids),
                    Message.sender_id != user_id,
                    Message.is_read == False
                ).order_by(desc(Message.created_at)).limit(20)
                
                result = db.execute(stmt)
                messages = result.scalars().unique().all()
                return messages
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting new messages for user {user_id}: {e}")
            return []
    
    async def get_message_history(self, user_id: int) -> List[Message]:
        """
        Получить историю сообщений пользователя
        """
        try:
            db = self._get_db()
            try:
                # Получаем заказы пользователя
                user_orders_stmt = select(Order.id).where(
                    (Order.creator_id == user_id) | 
                    (Order.proposals.any(Proposal.user_id == user_id))
                )
                
                user_orders_result = db.execute(user_orders_stmt)
                user_order_ids = [order.id for order in user_orders_result.scalars().all()]
                
                if not user_order_ids:
                    return []
                
                # Получаем все сообщения в заказах пользователя
                stmt = select(Message).options(
                    joinedload(Message.sender),
                    joinedload(Message.order)
                ).where(
                    Message.order_id.in_(user_order_ids)
                ).order_by(desc(Message.created_at)).limit(50)
                
                result = db.execute(stmt)
                messages = result.scalars().unique().all()
                return messages
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting message history for user {user_id}: {e}")
            return [] 