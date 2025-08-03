from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Optional
from app.models.message import Message
from app.models.order import Order
from app.models.user import User
from app.schemas.message import MessageCreate, MessageUpdate

class MessageCRUD:
    def create(self, db: Session, message: MessageCreate, sender_id: int) -> Message:
        # Проверяем, что заказ существует и пользователь имеет к нему доступ
        order = db.query(Order).filter(Order.id == message.order_id).first()
        if not order:
            raise ValueError("Order not found")
        
        # Проверяем, что отправитель и получатель имеют отношение к заказу
        if order.customer_id != sender_id and order.assigned_executor_id != sender_id:
            raise ValueError("You don't have access to this order")
        
        if order.customer_id != message.receiver_id and order.assigned_executor_id != message.receiver_id:
            raise ValueError("Receiver doesn't have access to this order")
        
        db_message = Message(
            order_id=message.order_id,
            sender_id=sender_id,
            receiver_id=message.receiver_id,
            content=message.content
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    def get_by_id(self, db: Session, message_id: int) -> Optional[Message]:
        return db.query(Message).filter(Message.id == message_id).first()

    def get_order_messages(self, db: Session, order_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        # Проверяем, что пользователь имеет доступ к заказу
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return []
        
        if order.customer_id != user_id and order.assigned_executor_id != user_id:
            return []
        
        return db.query(Message).filter(
            Message.order_id == order_id
        ).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()

    def get_conversation(self, db: Session, order_id: int, user_id: int, skip: int = 0, limit: int = 100) -> List[dict]:
        """Получить сообщения с именами пользователей"""
        messages = self.get_order_messages(db, order_id, user_id, skip, limit)
        
        result = []
        for message in messages:
            sender = db.query(User).filter(User.id == message.sender_id).first()
            receiver = db.query(User).filter(User.id == message.receiver_id).first()
            
            result.append({
                "id": message.id,
                "order_id": message.order_id,
                "sender_id": message.sender_id,
                "receiver_id": message.receiver_id,
                "content": message.content,
                "is_read": message.is_read,
                "created_at": message.created_at,
                "updated_at": message.updated_at,
                "sender_name": sender.full_name or sender.username if sender else "Unknown",
                "receiver_name": receiver.full_name or receiver.username if receiver else "Unknown"
            })
        
        return result

    def mark_as_read(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        """Отметить сообщение как прочитанное"""
        message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.receiver_id == user_id
            )
        ).first()
        
        if message:
            message.is_read = True
            db.commit()
            db.refresh(message)
        
        return message

    def mark_order_messages_as_read(self, db: Session, order_id: int, user_id: int) -> bool:
        """Отметить все сообщения заказа как прочитанные"""
        # Проверяем, что пользователь имеет доступ к заказу
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return False
        
        if order.customer_id != user_id and order.assigned_executor_id != user_id:
            return False
        
        # Отмечаем все непрочитанные сообщения как прочитанные
        db.query(Message).filter(
            and_(
                Message.order_id == order_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            )
        ).update({Message.is_read: True})
        
        db.commit()
        return True

    def get_unread_count(self, db: Session, user_id: int) -> int:
        """Получить количество непрочитанных сообщений пользователя"""
        return db.query(Message).filter(
            and_(
                Message.receiver_id == user_id,
                Message.is_read == False
            )
        ).count()

    def get_unread_count_by_order(self, db: Session, order_id: int, user_id: int) -> int:
        """Получить количество непрочитанных сообщений по конкретному заказу"""
        return db.query(Message).filter(
            and_(
                Message.order_id == order_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            )
        ).count()

    def delete(self, db: Session, message_id: int, user_id: int) -> bool:
        """Удалить сообщение (только отправитель может удалить)"""
        message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.sender_id == user_id
            )
        ).first()
        
        if not message:
            return False
        
        db.delete(message)
        db.commit()
        return True

message_crud = MessageCRUD() 