from sqlalchemy.orm import Session
from app.models.proposal import Proposal, ProposalStatus
from app.schemas.proposal import ProposalCreate, ProposalUpdate
from typing import Optional, List

class ProposalCRUD:
    def get_by_id(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        return db.query(Proposal).filter(Proposal.id == proposal_id).first()
    
    def get_by_order(self, db: Session, order_id: int, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).filter(Proposal.order_id == order_id).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).filter(Proposal.user_id == user_id).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_pending(self, db: Session, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).filter(Proposal.status == ProposalStatus.PENDING.value).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Proposal]:
        return db.query(Proposal).order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()
    
    def create(self, db: Session, proposal: ProposalCreate, user_id: int) -> Proposal:
        db_proposal = Proposal(
            description=proposal.description,
            price=proposal.price,
            estimated_duration=proposal.estimated_duration,
            order_id=proposal.order_id,
            user_id=user_id
        )
        db.add(db_proposal)
        db.commit()
        db.refresh(db_proposal)
        return db_proposal
    
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
    
    def accept(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return None
        
        db_proposal.status = ProposalStatus.ACCEPTED.value
        
        # Отклоняем все остальные предложения для этого заказа
        db.query(Proposal).filter(
            Proposal.order_id == db_proposal.order_id,
            Proposal.id != proposal_id,
            Proposal.status == ProposalStatus.PENDING.value
        ).update({Proposal.status: ProposalStatus.REJECTED.value})
        
        db.commit()
        db.refresh(db_proposal)
        return db_proposal
    
    def reject(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return None
        
        db_proposal.status = ProposalStatus.REJECTED.value
        
        db.commit()
        db.refresh(db_proposal)
        return db_proposal
    
    def withdraw(self, db: Session, proposal_id: int) -> Optional[Proposal]:
        db_proposal = self.get_by_id(db, proposal_id)
        if not db_proposal:
            return None
        
        db_proposal.status = ProposalStatus.WITHDRAWN.value
        
        db.commit()
        db.refresh(db_proposal)
        return db_proposal
    
    def check_owner(self, db: Session, proposal_id: int, user_id: int) -> bool:
        proposal = self.get_by_id(db, proposal_id)
        return proposal and proposal.user_id == user_id

proposal_crud = ProposalCRUD() 