import logging
from typing import List, Optional, Dict
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select

from app.database import get_db
from app.crud.order import order_crud
from app.crud.proposal import proposal_crud
from app.models.order import Order, OrderStatus
from app.models.proposal import Proposal, ProposalStatus
from app.models.user import User

logger = logging.getLogger(__name__)


class OrderService:
    """
    Сервис для работы с заказами
    """
    
    def __init__(self):
        pass
    
    def _get_db(self) -> Session:
        """Получить подключение к базе данных"""
        return next(get_db())
    
    async def get_available_orders(self) -> List[Order]:
        """Получить доступные заказы"""
        try:
            db = self._get_db()
            try:
                # Загружаем заказы с предзагруженными связанными данными
                stmt = select(Order).options(
                    joinedload(Order.creator)
                ).where(Order.status == OrderStatus.OPEN)
                result = db.execute(stmt)
                orders = result.scalars().unique().all()
                return orders
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting available orders: {e}")
            return []
    
    async def get_user_orders(self, user_id: int) -> List[Order]:
        """Получить заказы пользователя"""
        try:
            db = self._get_db()
            try:
                # Загружаем заказы с предзагруженными связанными данными
                stmt = select(Order).options(
                    joinedload(Order.creator)
                ).where(Order.creator_id == user_id)
                result = db.execute(stmt)
                orders = result.scalars().unique().all()
                return orders
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting user orders: {e}")
            return []
    
    async def get_user_proposals(self, user_id: int) -> List[Proposal]:
        """Получить предложения пользователя"""
        try:
            db = self._get_db()
            try:
                # Загружаем предложения с предзагруженными связанными данными
                stmt = select(Proposal).options(
                    joinedload(Proposal.order),
                    joinedload(Proposal.executor)
                ).where(Proposal.user_id == user_id)
                result = db.execute(stmt)
                proposals = result.scalars().unique().all()
                return proposals
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting user proposals: {e}")
            return []
    
    async def get_order_statistics(self, user_id: int) -> Dict:
        """Получить статистику заказов пользователя"""
        try:
            db = self._get_db()
            try:
                orders = order_crud.get_by_creator(db, creator_id=user_id)
                proposals = proposal_crud.get_by_user(db, user_id=user_id)
                
                stats = {
                    'total_orders': len(orders),
                    'total_proposals': len(proposals),
                    'accepted_proposals': len([p for p in proposals if p.status == ProposalStatus.ACCEPTED]),
                    'rejected_proposals': len([p for p in proposals if p.status == ProposalStatus.REJECTED]),
                    'total_earnings': sum(p.price for p in proposals if p.status == ProposalStatus.ACCEPTED)
                }
                
                return stats
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting order statistics: {e}")
            return {
                'total_orders': 0,
                'total_proposals': 0,
                'accepted_proposals': 0,
                'rejected_proposals': 0,
                'total_earnings': 0
            }
    
    async def get_order_by_id(self, order_id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        try:
            db = self._get_db()
            try:
                stmt = select(Order).options(
                    joinedload(Order.creator),
                    joinedload(Order.proposals).joinedload(Proposal.executor)
                ).where(Order.id == order_id)
                result = db.execute(stmt)
                order = result.scalar_one_or_none()
                return order
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting order by ID: {e}")
            return None
    
    async def delete_order(self, order_id: int, user_id: int) -> bool:
        """Удалить заказ"""
        try:
            db = self._get_db()
            try:
                # Получаем заказ
                order = order_crud.get(db, id=order_id)
                if not order:
                    return False
                
                # Проверяем права на удаление
                if order.creator_id != user_id:
                    return False
                
                # Удаляем заказ (все связанные предложения удалятся каскадно)
                success = order_crud.remove(db, id=order_id)
                return success
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error deleting order: {e}")
            return False
    
    async def complete_order(self, order_id: int, user_id: int) -> bool:
        """Завершить заказ"""
        try:
            db = self._get_db()
            try:
                # Получаем заказ
                order = order_crud.get(db, id=order_id)
                if not order:
                    return False
                
                # Проверяем права на завершение
                if order.creator_id != user_id:
                    return False
                
                # Проверяем, что заказ в работе
                if order.status != OrderStatus.IN_PROGRESS:
                    return False
                
                # Завершаем заказ
                order.status = OrderStatus.COMPLETED
                db.commit()
                return True
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error completing order: {e}")
            return False
    
    async def get_order_proposals(self, order_id: int) -> List[Proposal]:
        """Получить предложения к заказу"""
        try:
            db = self._get_db()
            try:
                stmt = select(Proposal).options(
                    joinedload(Proposal.executor),
                    joinedload(Proposal.order)
                ).where(Proposal.order_id == order_id)
                result = db.execute(stmt)
                proposals = result.scalars().unique().all()
                return proposals
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error getting order proposals: {e}")
            return []
    
    async def accept_proposal(self, proposal_id: int, user_id: int) -> bool:
        """Принять предложение к заказу"""
        try:
            db = self._get_db()
            try:
                # Получаем предложение
                proposal = proposal_crud.get(db, id=proposal_id)
                if not proposal:
                    return False
                
                # Проверяем, что пользователь является создателем заказа
                if proposal.order.creator_id != user_id:
                    return False
                
                # Принимаем предложение
                proposal.status = ProposalStatus.ACCEPTED
                
                # Переводим заказ в работу
                proposal.order.status = OrderStatus.IN_PROGRESS
                proposal.order.executor_id = proposal.executor_id
                
                # Отклоняем все остальные предложения к этому заказу
                other_proposals = proposal_crud.get_by_order(db, order_id=proposal.order_id)
                for other_proposal in other_proposals:
                    if other_proposal.id != proposal_id:
                        other_proposal.status = ProposalStatus.REJECTED
                
                db.commit()
                return True
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error accepting proposal: {e}")
            return False
    
    async def reject_proposal(self, proposal_id: int, user_id: int) -> bool:
        """Отклонить предложение к заказу"""
        try:
            db = self._get_db()
            try:
                # Получаем предложение
                proposal = proposal_crud.get(db, id=proposal_id)
                if not proposal:
                    return False
                
                # Проверяем, что пользователь является создателем заказа
                if proposal.order.creator_id != user_id:
                    return False
                
                # Отклоняем предложение
                proposal.status = ProposalStatus.REJECTED
                db.commit()
                return True
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error rejecting proposal: {e}")
            return False
    
    async def create_order(self, order_data: Dict, user_id: int) -> Optional[Order]:
        """Создать новый заказ"""
        try:
            from app.schemas.order import OrderCreate
            order_create = OrderCreate(**order_data)
            db = self._get_db()
            try:
                return order_crud.create(db, order=order_create, creator_id=user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error creating order: {e}")
            return None
    
    async def create_proposal(self, proposal_data: Dict, user_id: int) -> Optional[Proposal]:
        """Создать новое предложение"""
        try:
            from app.schemas.proposal import ProposalCreate
            proposal_create = ProposalCreate(**proposal_data)
            db = self._get_db()
            try:
                return proposal_crud.create(db, proposal=proposal_create, user_id=user_id)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error creating proposal: {e}")
            return None
    
    async def update_order(self, order_id: int, order_data: dict) -> bool:
        """Обновить заказ"""
        try:
            from app.schemas.order import OrderUpdate
            order_update = OrderUpdate(**order_data)
            db = self._get_db()
            try:
                return order_crud.update(db, order_id=order_id, order_update=order_update)
            finally:
                db.close()
        except Exception as e:
            logger.error(f"Error updating order: {e}")
            return False 