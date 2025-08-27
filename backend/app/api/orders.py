from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.order import order_crud
from app.crud.proposal import proposal_crud
from app.schemas.order import OrderCreate, OrderUpdate, OrderResponse, OrderWithProposals, OrderStats
from app.schemas.proposal import ProposalResponse
from app.auth.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.order import OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])

@router.post("/", response_model=OrderResponse)
def create_order(
    order: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Создать новый заказ (для заказчиков и администраторов)"""
    if current_user.role not in [UserRole.CUSTOMER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers and admins can create orders"
        )
    
    try:
        return order_crud.create(db=db, order=order, creator_id=current_user.id)
    except Exception as e:
        logger.error(f"Error creating order: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating order: {str(e)}"
        )

@router.get("/", response_model=List[OrderWithProposals])
def read_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить все заказы (для администраторов и исполнителей)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.EXECUTOR]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    orders = order_crud.get_all(db, skip=skip, limit=limit)
    
    # Добавляем предложения для каждого заказа
    for order in orders:
        order.proposals = proposal_crud.get_by_order(db, order_id=order.id)
    
    return orders

@router.get("/open", response_model=List[OrderWithProposals])
def read_open_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить открытые заказы (для исполнителей)"""
    if current_user.role != UserRole.EXECUTOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only executors can view open orders"
        )
    
    orders = order_crud.get_open_orders(db, skip=skip, limit=limit)
    
    # Добавляем предложения для каждого заказа
    for order in orders:
        order.proposals = proposal_crud.get_by_order(db, order_id=order.id)
    
    return orders

@router.get("/my", response_model=List[OrderWithProposals])
def read_my_orders(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить заказы текущего пользователя"""
    orders = []
    
    if current_user.role == UserRole.CUSTOMER:
        orders = order_crud.get_by_customer(db, creator_id=current_user.id, skip=skip, limit=limit)
    elif current_user.role == UserRole.EXECUTOR:
        orders = order_crud.get_by_executor(db, executor_id=current_user.id, skip=skip, limit=limit)
    elif current_user.role == UserRole.ADMIN:
        # Администраторы видят все заказы
        orders = order_crud.get_all(db, skip=skip, limit=limit)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Invalid user role: {current_user.role}"
        )
    
    # Добавляем предложения для каждого заказа
    for order in orders:
        order.proposals = proposal_crud.get_by_order(db, order_id=order.id)
    
    return orders

@router.get("/{order_id}", response_model=OrderWithProposals)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить заказ по ID с предложениями"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Проверяем права доступа
    if current_user.role == UserRole.CUSTOMER and order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Получаем предложения для заказа
    proposals = proposal_crud.get_by_order(db, order_id=order_id)
    
    # Создаем ответ с предложениями
    order_dict = {
        "id": order.id,
        "title": order.title,
        "description": order.description,
        "budget": order.budget,
        "deadline": order.deadline,
        "priority": order.priority,
        "status": order.status,
        "tags": order.tags,
        "creator_id": order.creator_id,
        "assigned_executor_id": order.assigned_executor_id,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
        "completed_at": order.completed_at,
        "proposals": proposals
    }
    
    return order_dict

@router.put("/{order_id}", response_model=OrderResponse)
def update_order(
    order_id: int,
    order_update: OrderUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Обновить заказ (только владелец заказа)"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return order_crud.update(db, order_id=order_id, order_update=order_update)

@router.delete("/{order_id}")
def delete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить заказ (только владелец заказа)"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = order_crud.delete(db, order_id=order_id)
    if not success:
        raise HTTPException(status_code=404, detail="Order not found")
    return {"message": "Order deleted successfully"}

@router.post("/{order_id}/complete", response_model=OrderResponse)
def complete_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Завершить заказ (только владелец заказа)"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if order.status != OrderStatus.IN_PROGRESS.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be in progress to complete"
        )
    
    return order_crud.complete_order(db, order_id=order_id)

@router.post("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отменить заказ (только владелец заказа)"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if order.status not in [OrderStatus.OPEN.value, OrderStatus.IN_PROGRESS.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order cannot be cancelled in current status"
        )
    
    return order_crud.cancel_order(db, order_id=order_id)

@router.post("/{order_id}/restore", response_model=OrderResponse)
def restore_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Восстановить отмененный заказ (только владелец заказа)"""
    order = order_crud.get_by_id(db, order_id=order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    if order.status != OrderStatus.CANCELLED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order must be cancelled to restore"
        )
    
    return order_crud.restore_order(db, order_id=order_id)

@router.get("/stats/my", response_model=OrderStats)
def get_my_order_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить статистику заказов пользователя"""
    if current_user.role == UserRole.CUSTOMER:
        return order_crud.get_stats(db, creator_id=current_user.id)
    elif current_user.role == UserRole.ADMIN:
        # Администраторы видят общую статистику
        return order_crud.get_stats(db)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers and admins can view order stats"
        ) 