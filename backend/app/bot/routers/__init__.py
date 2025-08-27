from aiogram import Dispatcher
from .start_router import router as start_router
from .auth_router import router as auth_router
from .registration_router import router as registration_router
from .tasks_router import router as tasks_router
from .orders_router import router as orders_router
from .profile_router import router as profile_router
from .admin_router import router as admin_router
from .chat_router import router as chat_router
from .order_creation_router import router as order_creation_router
from .task_creation_router import router as task_creation_router
from .settings_router import router as settings_router


def register_routers(dp: Dispatcher):
    """
    Регистрируем все роутеры в диспетчере
    """
    dp.include_router(start_router)
    dp.include_router(registration_router)
    dp.include_router(auth_router)
    dp.include_router(orders_router)
    dp.include_router(tasks_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)
    dp.include_router(chat_router)
    dp.include_router(order_creation_router)
    dp.include_router(task_creation_router)
    dp.include_router(settings_router) 