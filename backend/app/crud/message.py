from sqlalchemy.orm import Session
from app.models.message import Message
from app.schemas.message import MessageCreate, MessageUpdate
from typing import Optional, List

class MessageCRUD:
    def get_by_id(self, db: Session, message_id: int) -> Optional[Message]:
        return db.query(Message).filter(Message.id == message_id).first()
    
    def get_by_order(self, db: Session, order_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(Message.order_id == order_id).order_by(Message.created_at.asc()).offset(skip).limit(limit).all()
    
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).filter(
            (Message.sender_id == user_id) | (Message.receiver_id == user_id)
        ).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_unread_count(self, db: Session, user_id: int) -> int:
        return db.query(Message).filter(
            Message.receiver_id == user_id,
            Message.is_read == False
        ).count()
    
    def get_order_unread_count(self, db: Session, order_id: int, user_id: int) -> int:
        return db.query(Message).filter(
            Message.order_id == order_id,
            Message.receiver_id == user_id,
            Message.is_read == False
        ).count()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Message]:
        return db.query(Message).order_by(Message.created_at.desc()).offset(skip).limit(limit).all()
    
    def create(self, db: Session, message: MessageCreate, sender_id: int) -> Message:
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
    
    def update(self, db: Session, message_id: int, message_update: MessageUpdate) -> Optional[Message]:
        db_message = self.get_by_id(db, message_id)
        if not db_message:
            return None
        
        update_data = message_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_message, field, value)
        
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def delete(self, db: Session, message_id: int) -> bool:
        db_message = self.get_by_id(db, message_id)
        if not db_message:
            return False
        
        db.delete(db_message)
        db.commit()
        return True
    
    def mark_as_read(self, db: Session, message_id: int) -> Optional[Message]:
        db_message = self.get_by_id(db, message_id)
        if not db_message:
            return None
        
        db_message.is_read = True
        
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def mark_order_as_read(self, db: Session, order_id: int, user_id: int) -> bool:
        """Отметить все сообщения заказа как прочитанные для конкретного пользователя"""
        try:
            db.query(Message).filter(
                Message.order_id == order_id,
                Message.receiver_id == user_id,
                Message.is_read == False
            ).update({Message.is_read: True})
            
            db.commit()
            return True
        except Exception:
            db.rollback()
            return False
    
    def check_owner(self, db: Session, message_id: int, user_id: int) -> bool:
        message = self.get_by_id(db, message_id)
        return message and message.sender_id == user_id

message_crud = MessageCRUD() 