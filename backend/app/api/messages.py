from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.crud.message import message_crud
from app.schemas.message import MessageCreate, MessageResponse, MessageWithUsers
from app.auth.dependencies import get_current_active_user
from app.models.user import User, UserRole
from app.models.order import Order

router = APIRouter(prefix="/messages", tags=["messages"])

@router.post("/", response_model=MessageResponse)
def create_message(
    message: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отправить сообщение (только участники заказа)"""
    try:
        return message_crud.create(db=db, message=message, sender_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/order/{order_id}", response_model=List[MessageWithUsers])
def get_order_messages(
    order_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить сообщения по заказу (только участники заказа)"""
    # Проверяем, что заказ существует
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Проверяем, что пользователь имеет доступ к заказу
    if order.customer_id != current_user.id and order.assigned_executor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Отмечаем сообщения как прочитанные
    message_crud.mark_order_messages_as_read(db, order_id, current_user.id)
    
    return message_crud.get_conversation(db, order_id, current_user.id, skip, limit)

@router.get("/unread/count")
def get_unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить количество непрочитанных сообщений"""
    count = message_crud.get_unread_count(db, current_user.id)
    return {"unread_count": count}

@router.get("/order/{order_id}/unread/count")
def get_order_unread_count(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Получить количество непрочитанных сообщений по заказу"""
    # Проверяем, что заказ существует
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Проверяем, что пользователь имеет доступ к заказу
    if order.customer_id != current_user.id and order.assigned_executor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    count = message_crud.get_unread_count_by_order(db, order_id, current_user.id)
    return {"unread_count": count}

@router.post("/{message_id}/read")
def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отметить сообщение как прочитанное"""
    message = message_crud.mark_as_read(db, message_id, current_user.id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    
    return {"message": "Message marked as read"}

@router.post("/order/{order_id}/read")
def mark_order_messages_as_read(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Отметить все сообщения заказа как прочитанные"""
    # Проверяем, что заказ существует
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Проверяем, что пользователь имеет доступ к заказу
    if order.customer_id != current_user.id and order.assigned_executor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    success = message_crud.mark_order_messages_as_read(db, order_id, current_user.id)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to mark messages as read")
    
    return {"message": "All messages marked as read"}

@router.delete("/{message_id}")
def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Удалить сообщение (только отправитель)"""
    success = message_crud.delete(db, message_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Message not found or not enough permissions")
    
    return {"message": "Message deleted successfully"} 