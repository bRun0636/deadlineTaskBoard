from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict
from app.models.proposal import Proposal, ProposalStatus
from app.models.order import Order, OrderStatus
from app.models.user import User, UserRole
from app.schemas.proposal import ProposalCreate, ProposalUpdate

class ProposalCRUD:
    def create(self, db: Session, proposal: ProposalCreate, executor_id: int) -> Proposal:
        # Проверяем, что заказ существует и открыт
        order = db.query(Order).filter(Order.id == proposal.order_id).first()
        if not order or order.status != OrderStatus.OPEN.value:
            raise ValueError("Order not found or not open")

        # Проверяем, что пользователь является исполнителем
        executor = db.query(User).filter(User.id == executor_id, User.role == UserRole.EXECUTOR.value).first()
        if not executor:
            raise ValueError("User is not an executor")

        # Проверяем, что исполнитель еще не делал предложение по этому заказу
        existing_proposal = db.query(Proposal).filter(
            Proposal.order_id == proposal.order_id,
            Proposal.user_id == executor_id
        ).first()
        if existing_proposal:
            raise ValueError("Proposal already exists for this order")

        db_proposal = Proposal(
            description=proposal.description,
            price=proposal.price,
            estimated_duration=proposal.estimated_duration,
            order_id=proposal.order_id,
            user_id=executor_id
        )
        db.add(db_proposal)
        db.commit()
        db.refresh(db_proposal)
        return db_proposal

    def get_by_id(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        return db.query(Proposal).filter(Proposal.id == proposal_id).first()

    def get_by_order(self, db: Session, order_id: int, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).filter(Proposal.order_id == order_id).offset(skip).limit(limit).all()

    def get_by_executor(self, db: Session, executor_id: int, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).filter(Proposal.user_id == executor_id).offset(skip).limit(limit).all()

    def get_pending_by_executor(self, db: Session, executor_id: int, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).filter(
            Proposal.user_id == executor_id,
            Proposal.status == ProposalStatus.PENDING.value
        ).offset(skip).limit(limit).all()

    def update(self, db: Session, proposal_id: int, proposal_update: ProposalUpdate) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return None

        update_data = proposal_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_proposal, field, value)

        db.commit()
        db.refresh(db_proposal)
        return db_proposal

    def delete(self, db: Session, proposal_id: int) -> bool:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return False

        db.delete(db_proposal)
        db.commit()
        return True

    def accept_proposal(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return None

        # Проверяем, что заказ еще открыт
        order = db.query(Order).filter(Order.id == db_proposal.order_id).first()
        if not order or order.status != OrderStatus.OPEN.value:
            return None

        # Принимаем предложение
        db_proposal.status = ProposalStatus.ACCEPTED.value

        # Назначаем исполнителя на заказ
        order.assigned_executor_id = db_proposal.user_id
        order.status = OrderStatus.IN_PROGRESS.value

        # Отклоняем все остальные предложения по этому заказу
        db.query(Proposal).filter(
            Proposal.order_id == db_proposal.order_id,
            Proposal.id != proposal_id,
            Proposal.status == ProposalStatus.PENDING.value
        ).update({Proposal.status: ProposalStatus.REJECTED.value})

        db.commit()
        db.refresh(db_proposal)
        return db_proposal

    def reject_proposal(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return None

        db_proposal.status = ProposalStatus.REJECTED.value
        db.commit()
        db.refresh(db_proposal)
        return db_proposal

    def withdraw_proposal(self, db: Session, proposal_id: int, executor_id: int) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal or db_proposal.user_id != executor_id:
            return None

        # Проверяем, что предложение еще не принято
        if db_proposal.status == ProposalStatus.ACCEPTED.value:
            return None

        db_proposal.status = ProposalStatus.WITHDRAWN.value
        db.commit()
        db.refresh(db_proposal)
        return db_proposal

    def get_stats(self, db: Session, executor_id: Optional[int] = None) -> Dict:
        query = db.query(Proposal)
        if executor_id:
            query = query.filter(Proposal.user_id == executor_id)

        total_proposals = query.count()
        pending_proposals = query.filter(Proposal.status == ProposalStatus.PENDING.value).count()
        accepted_proposals = query.filter(Proposal.status == ProposalStatus.ACCEPTED.value).count()
        rejected_proposals = query.filter(Proposal.status == ProposalStatus.REJECTED.value).count()
        
        price_stats = query.with_entities(
            func.avg(Proposal.price).label('average_price')
        ).first()

        return {
            "total_proposals": total_proposals,
            "pending_proposals": pending_proposals,
            "accepted_proposals": accepted_proposals,
            "rejected_proposals": rejected_proposals,
            "average_price": float(price_stats.average_price or 0)
        }

proposal_crud = ProposalCRUD() 