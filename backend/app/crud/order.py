from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus, OrderPriority
from app.schemas.order import OrderCreate, OrderUpdate
from typing import Optional, List

class OrderCRUD:
    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()
    
    def get_by_creator(self, db: Session, creator_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.creator_id == creator_id).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_open_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.status == OrderStatus.OPEN.value).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    
    def create(self, db: Session, order: OrderCreate, creator_id: int) -> Order:
        db_order = Order(
            title=order.title,
            description=order.description,
            budget=order.budget,
            deadline=order.deadline,
            priority=order.priority.value if order.priority else OrderPriority.MEDIUM.value,
            tags=','.join(order.tags) if order.tags else None,
            creator_id=creator_id
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def update(self, db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None
        
        update_data = order_update.dict(exclude_unset=True)
        
        # Конвертируем tags из списка в строку, если они есть
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = ','.join(update_data['tags'])
        
        # Конвертируем priority enum в строку
        if 'priority' in update_data and update_data['priority'] is not None:
            update_data['priority'] = update_data['priority'].value
        
        for field, value in update_data.items():
            setattr(db_order, field, value)
        
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def delete(self, db: Session, order_id: int) -> bool:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return False
        
        db.delete(db_order)
        db.commit()
        return True
    
    def complete(self, db: Session, order_id: int, executor_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None
        
        db_order.status = OrderStatus.COMPLETED.value
        db_order.assigned_executor_id = executor_id
        db_order.completed_at = db.func.now()
        
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def cancel(self, db: Session, order_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None
        
        db_order.status = OrderStatus.CANCELLED.value
        
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def restore(self, db: Session, order_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None
        
        db_order.status = OrderStatus.OPEN.value
        
        db.commit()
        db.refresh(db_order)
        return db_order
    
    def check_owner(self, db: Session, order_id: int, user_id: int) -> bool:
        order = self.get_by_id(db, order_id)
        return order and order.creator_id == user_id

order_crud = OrderCRUD() 