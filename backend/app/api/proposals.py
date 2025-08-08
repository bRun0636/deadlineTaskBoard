from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.proposal import proposal_crud
from app.crud.order import order_crud
from app.schemas.proposal import ProposalCreate, ProposalUpdate, ProposalResponse, ProposalStats
from app.auth.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.proposal import ProposalStatus

router = APIRouter(prefix="/proposals", tags=["proposals"])

@router.post("/", response_model=ProposalResponse)
def create_proposal(
    proposal: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать предложение по заказу (для исполнителей и администраторов)"""
    if current_user.role not in [UserRole.EXECUTOR.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only executors and admins can create proposals"
        )
    
    # Проверяем, что администратор не создает предложение на свой собственный заказ
    if current_user.role == UserRole.ADMIN.value:
        order = order_crud.get_by_id(db, order_id=proposal.order_id)
        if order and order.creator_id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admins cannot create proposals for their own orders"
            )
    
    try:
        return proposal_crud.create(db=db, proposal=proposal, executor_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[ProposalResponse])
def read_proposals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить все предложения (для администраторов)"""
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can view all proposals"
        )
    
    return proposal_crud.get_by_executor(db, executor_id=current_user.id, skip=skip, limit=limit)

@router.get("/my", response_model=List[ProposalResponse])
def read_my_proposals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить предложения текущего пользователя"""
    if current_user.role not in [UserRole.EXECUTOR.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only executors and admins can view their proposals"
        )
    
    return proposal_crud.get_by_executor(db, executor_id=current_user.id, skip=skip, limit=limit)

@router.get("/pending", response_model=List[ProposalResponse])
def read_pending_proposals(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить ожидающие предложения пользователя"""
    if current_user.role not in [UserRole.EXECUTOR.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only executors and admins can view pending proposals"
        )
    
    return proposal_crud.get_pending_by_executor(db, executor_id=current_user.id, skip=skip, limit=limit)

@router.get("/order/{order_id}", response_model=List[ProposalResponse])
def read_order_proposals(
    order_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить предложения по заказу (владелец заказа или администратор)"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Владелец заказа или администратор могут видеть предложения
    if order.creator_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return proposal_crud.get_by_order(db, order_id=order_id, skip=skip, limit=limit)

@router.get("/{proposal_id}", response_model=ProposalResponse)
def read_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить предложение по ID"""
    proposal = proposal_crud.get_by_id(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    # Проверяем права доступа
    order = order_crud.get_by_id(db, order_id=proposal.order_id)
    if current_user.role == UserRole.EXECUTOR.value and proposal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    elif current_user.role == UserRole.CUSTOMER.value and order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return proposal

@router.put("/{proposal_id}", response_model=ProposalResponse)
def update_proposal(
    proposal_id: int,
    proposal_update: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить предложение (только автор предложения)"""
    proposal = proposal_crud.get_by_id(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if proposal.status != ProposalStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update pending proposals"
        )
    
    return proposal_crud.update(db, proposal_id=proposal_id, proposal_update=proposal_update)

@router.delete("/{proposal_id}")
def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить предложение (только автор предложения)"""
    proposal = proposal_crud.get_by_id(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    if proposal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = proposal_crud.delete(db, proposal_id=proposal_id)
    if not success:
        raise HTTPException(status_code=404, detail="Proposal not found")
    return {"message": "Proposal deleted successfully"}

@router.post("/{proposal_id}/accept", response_model=ProposalResponse)
def accept_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Принять предложение (владелец заказа или администратор)"""
    proposal = proposal_crud.get_by_id(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    order = order_crud.get_by_id(db, order_id=proposal.order_id)
    # Владелец заказа или администратор могут принимать предложения
    if order.creator_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return proposal_crud.accept_proposal(db, proposal_id=proposal_id)

@router.post("/{proposal_id}/reject", response_model=ProposalResponse)
def reject_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отклонить предложение (владелец заказа или администратор)"""
    proposal = proposal_crud.get_by_id(db, proposal_id=proposal_id)
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")
    
    order = order_crud.get_by_id(db, order_id=proposal.order_id)
    # Владелец заказа или администратор могут отклонять предложения
    if order.creator_id != current_user.id and current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return proposal_crud.reject_proposal(db, proposal_id=proposal_id)

@router.post("/{proposal_id}/withdraw", response_model=ProposalResponse)
def withdraw_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отозвать предложение (автор предложения)"""
    if current_user.role not in [UserRole.EXECUTOR.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only executors and admins can withdraw proposals"
        )
    
    return proposal_crud.withdraw_proposal(db, proposal_id=proposal_id, executor_id=current_user.id)

@router.get("/stats/my", response_model=ProposalStats)
def get_my_proposal_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить статистику предложений пользователя"""
    if current_user.role not in [UserRole.EXECUTOR.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only executors and admins can view proposal stats"
        )
    
    return proposal_crud.get_stats(db, executor_id=current_user.id) 