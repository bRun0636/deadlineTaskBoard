from aiogram import Dispatcher
from .auth_middleware import AuthMiddleware


def register_middlewares(dp: Dispatcher):
    """
    Регистрируем все middleware в диспетчере
    """
    # Регистрируем middleware для всех типов обновлений
    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware()) 