from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from app.models.order import Order, OrderStatus
from app.models.proposal import Proposal, ProposalStatus
from app.models.user import User, UserRole
from app.schemas.order import OrderCreate, OrderUpdate

class OrderCRUD:
    def create(self, db: Session, order: OrderCreate, customer_id: int) -> Order:
        db_order = Order(
            title=order.title,
            description=order.description,
            budget=order.budget,
            deadline=order.deadline,
            priority=order.priority,
            tags=order.tags,
            customer_id=customer_id
        )
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return db_order

    def get_by_id(self, db: Session, order_id: int) -> Optional[Order]:
        return db.query(Order).filter(Order.id == order_id).first()

    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).offset(skip).limit(limit).all()

    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.customer_id == customer_id).offset(skip).limit(limit).all()

    def get_open_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.status == OrderStatus.OPEN).offset(skip).limit(limit).all()

    def get_by_executor(self, db: Session, executor_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        return db.query(Order).filter(Order.assigned_executor_id == executor_id).offset(skip).limit(limit).all()

    def update(self, db: Session, order_id: int, order_update: OrderUpdate) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None

        update_data = order_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            # Обрабатываем enum поля
            if field == 'priority' and hasattr(value, 'value'):
                setattr(db_order, field, value.value)
            elif field == 'status' and hasattr(value, 'value'):
                setattr(db_order, field, value.value)
            else:
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

    def assign_executor(self, db: Session, order_id: int, executor_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None

        # Проверяем, что пользователь является исполнителем
        executor = db.query(User).filter(User.id == executor_id, User.role == UserRole.EXECUTOR).first()
        if not executor:
            return None

        db_order.assigned_executor_id = executor_id
        db_order.status = OrderStatus.IN_PROGRESS

        # Отклоняем все остальные предложения
        db.query(Proposal).filter(
            Proposal.order_id == order_id,
            Proposal.status == ProposalStatus.PENDING
        ).update({Proposal.status: ProposalStatus.REJECTED})

        db.commit()
        db.refresh(db_order)
        return db_order

    def complete_order(self, db: Session, order_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None

        db_order.status = OrderStatus.COMPLETED
        db_order.completed_at = func.now()

        db.commit()
        db.refresh(db_order)
        return db_order

    def cancel_order(self, db: Session, order_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None

        db_order.status = OrderStatus.CANCELLED

        # Отклоняем все предложения
        db.query(Proposal).filter(
            Proposal.order_id == order_id,
            Proposal.status == ProposalStatus.PENDING
        ).update({Proposal.status: ProposalStatus.REJECTED})

        db.commit()
        db.refresh(db_order)
        return db_order

    def restore_order(self, db: Session, order_id: int) -> Optional[Order]:
        db_order = self.get_by_id(db, order_id)
        if not db_order:
            return None

        # Восстанавливаем заказ в статус "открыт"
        db_order.status = OrderStatus.OPEN
        db_order.assigned_executor_id = None  # Сбрасываем исполнителя
        db_order.completed_at = None  # Сбрасываем дату завершения

        db.commit()
        db.refresh(db_order)
        return db_order

    def get_stats(self, db: Session, customer_id: Optional[int] = None) -> Dict:
        query = db.query(Order)
        if customer_id:
            query = query.filter(Order.customer_id == customer_id)

        total_orders = query.count()
        open_orders = query.filter(Order.status == OrderStatus.OPEN).count()
        in_progress_orders = query.filter(Order.status == OrderStatus.IN_PROGRESS).count()
        completed_orders = query.filter(Order.status == OrderStatus.COMPLETED).count()
        
        budget_stats = query.with_entities(
            func.sum(Order.budget).label('total_budget'),
            func.avg(Order.budget).label('average_budget')
        ).first()

        return {
            "total_orders": total_orders,
            "open_orders": open_orders,
            "in_progress_orders": in_progress_orders,
            "completed_orders": completed_orders,
            "total_budget": float(budget_stats.total_budget or 0),
            "average_budget": float(budget_stats.average_budget or 0)
        }

order_crud = OrderCRUD() 