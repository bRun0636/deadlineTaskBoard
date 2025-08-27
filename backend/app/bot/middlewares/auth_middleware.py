import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery

from ..services.user_service import UserService

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """
    Middleware для проверки аутентификации пользователей
    """
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """
        Обработка события с проверкой аутентификации
        """
        try:
            # Получаем информацию о пользователе из Telegram
            if isinstance(event, Message):
                telegram_user = event.from_user
            else:
                telegram_user = event.from_user
            
            # Добавляем информацию о пользователе в данные
            data["telegram_user"] = telegram_user
            
            # Получаем или создаем пользователя из базы данных
            user_service = UserService()
            user = await user_service.get_or_create_user(
                telegram_id=telegram_user.id,
                username=telegram_user.username,
                first_name=telegram_user.first_name,
                last_name=telegram_user.last_name
            )
            
            # Добавляем пользователя в данные
            data["user"] = user
            
            # Логируем информацию о пользователе
            logger.info(f"User {telegram_user.id} ({telegram_user.username}) - registered: {user.is_registered if user else False}")
            
        except Exception as e:
            logger.error(f"Error in AuthMiddleware: {e}")
            # В случае ошибки продолжаем выполнение без пользователя
            data["user"] = None
        
        # Вызываем следующий обработчик
        return await handler(event, data) 