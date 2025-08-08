import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, UserRole

logger = logging.getLogger(__name__)


class UserService:
    """
    Сервис для работы с пользователями
    """
    
    def __init__(self):
        self.db: Session = next(get_db())
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """
        Получить пользователя по Telegram ID
        """
        try:
            stmt = select(User).where(User.telegram_id == telegram_id)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()
            return user
        except Exception as e:
            logger.error(f"Error getting user by telegram_id {telegram_id}: {e}")
            return None
    
    async def get_or_create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        """
        Получить или создать пользователя
        """
        try:
            # Проверяем, существует ли пользователь
            user = await self.get_user_by_telegram_id(telegram_id)
            
            if user:
                # Обновляем только Telegram-информацию о пользователе
                if username:
                    user.telegram_username = username  # Обновляем только telegram_username
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                
                # НЕ обновляем основной username пользователя, чтобы сохранить его веб-аккаунт
                
                self.db.commit()
                return user
            
            # Создаем нового пользователя
            # Telegram пользователи не имеют email
            
            # Генерируем уникальный username для Telegram пользователя
            generated_username = f"tg_user_{telegram_id}"
            
            user = User(
                telegram_id=telegram_id,
                username=generated_username,  # Используем сгенерированный username
                telegram_username=username,  # Сохраняем оригинальный telegram_username
                email=None,  # Telegram пользователи не имеют email
                first_name=first_name,
                last_name=last_name,
                hashed_password=User.get_password_hash("telegram_user_default_password"),  # Хешированный пароль для Telegram пользователей
                is_registered=False,
                is_active=True,
                role="executor"  # Используем строку в нижнем регистре
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Created new user with telegram_id {telegram_id}")
            return user
            
        except Exception as e:
            logger.error(f"Error creating user with telegram_id {telegram_id}: {e}")
            self.db.rollback()
            raise
    
    async def update_user_telegram_id(self, user_id: int, telegram_id: int) -> bool:
        """
        Обновить Telegram ID пользователя
        """
        try:
            stmt = select(User).where(User.id == user_id)
            result = self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if user:
                user.telegram_id = telegram_id
                self.db.commit()
                logger.info(f"Updated telegram_id for user {user_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating telegram_id for user {user_id}: {e}")
            self.db.rollback()
            return False
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """
        Получить статистику пользователя
        """
        try:
            # Здесь можно добавить логику получения статистики
            # Пока возвращаем базовую структуру
            return {
                'tasks_created': 0,
                'tasks_completed': 0,
                'orders_created': 0,
                'orders_completed': 0,
                'messages_sent': 0,
                'proposals_received': 0
            }
        except Exception as e:
            logger.error(f"Error getting statistics for user {user_id}: {e}")
            return {}

    async def complete_registration(self, telegram_id: int, registration_data: Dict[str, Any]) -> bool:
        """
        Завершить регистрацию пользователя
        """
        try:
            user = await self.get_user_by_telegram_id(telegram_id)
            if not user:
                logger.error(f"User with telegram_id {telegram_id} not found")
                return False
            
            # Проверяем, что user является экземпляром модели User
            if not hasattr(user, 'set_payment_types_list'):
                logger.error(f"User object does not have required methods. User type: {type(user)}")
                return False
            
            # Обновляем данные пользователя
            user.phone = registration_data.get('phone')
            user.country = registration_data.get('country')
            
            # Приводим enum значения к нижнему регистру
            juridical_type = registration_data.get('juridical_type')
            if juridical_type:
                if hasattr(juridical_type, 'value'):
                    user.juridical_type = juridical_type.value.lower()
                elif isinstance(juridical_type, str):
                    user.juridical_type = juridical_type.lower()
            
            prof_level = registration_data.get('prof_level')
            if prof_level:
                if hasattr(prof_level, 'value'):
                    user.prof_level = prof_level.value.lower()
                elif isinstance(prof_level, str):
                    user.prof_level = prof_level.lower()
            
            user.bio = registration_data.get('bio')
            user.is_registered = True
            
            # Устанавливаем роль
            role = registration_data.get('role')
            if role:
                if hasattr(role, 'value'):
                    user.role = role.value.lower()
                elif isinstance(role, str):
                    user.role = role.lower()
            
            # Устанавливаем типы оплаты
            payment_types = registration_data.get('payment_types', [])
            if payment_types:
                user.set_payment_types_list(payment_types)
            
            # Устанавливаем навыки
            skills = registration_data.get('skills', [])
            if skills:
                user.set_skills_list(skills)
            
            # Устанавливаем типы уведомлений
            notification_types = registration_data.get('notification_types', [])
            if notification_types:
                user.set_notification_types_list(notification_types)
            
            self.db.commit()
            logger.info(f"Registration completed for user {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing registration for user {telegram_id}: {e}")
            self.db.rollback()
            return False
    
    def __del__(self):
        """
        Закрываем соединение с БД
        """
        if hasattr(self, 'db'):
            self.db.close() 