import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..keyboards.admin_keyboards import get_admin_keyboard
from ..services.admin_service import AdminService
from ..services.user_service import UserService
from app.models.user import UserRole

router = Router(name="admin_router")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "admin")
async def admin_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик админского меню
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_registered or user.role != UserRole.ADMIN.value:
        await callback.message.edit_text(
            "❌ Доступ запрещен.\n\n"
            "Эта функция доступна только администраторам.",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🔧 <b>Админ-панель</b>\n\n"
        "Выберите действие:",
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_users")
async def admin_users_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик просмотра пользователей (админ)
    """
    user_service = UserService()
    admin_service = AdminService()
    
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_registered or user.role != UserRole.ADMIN.value:
        await callback.message.edit_text(
            "❌ Доступ запрещен.\n\n"
            "Эта функция доступна только администраторам.",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()
        return
    
    users = await admin_service.get_all_users()
    
    users_text = "👥 <b>Пользователи</b>\n\n"
    for i, u in enumerate(users[:10], 1):  # Показываем первые 10 пользователей
        users_text += (
            f"{i}. 👤 <b>{u.first_name or u.username or 'Без имени'}</b>\n"
            f"   Email: {u.email or 'Не указан'}\n"
            f"   Роль: {u.role or 'Не указана'}\n"
            f"   Статус: {'✅ Активен' if u.is_active else '❌ Неактивен'}\n\n"
        )
    
    if len(users) > 10:
        users_text += f"... и еще {len(users) - 10} пользователей\n\n"
    
    users_text += "🌐 <a href='http://localhost:3000/admin'>Управление пользователями на сайте</a>"
    
    await callback.message.edit_text(
        users_text,
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "admin_stats")
async def admin_stats_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик статистики (админ)
    """
    user_service = UserService()
    admin_service = AdminService()
    
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_registered or user.role != UserRole.ADMIN.value:
        await callback.message.edit_text(
            "❌ Доступ запрещен.\n\n"
            "Эта функция доступна только администраторам.",
            reply_markup=get_admin_keyboard()
        )
        await callback.answer()
        return
    
    stats = await admin_service.get_system_statistics()
    
    stats_text = (
        f"📊 <b>Статистика системы</b>\n\n"
        f"Пользователей: {stats.get('total_users', 0)}\n"
        f"Активных пользователей: {stats.get('active_users', 0)}\n"
        f"Задач: {stats.get('total_tasks', 0)}\n"
        f"Заказов: {stats.get('total_orders', 0)}\n"
        f"Сообщений: {stats.get('total_messages', 0)}\n"
        f"Предложений: {stats.get('total_proposals', 0)}\n\n"
        f"🌐 <a href='http://localhost:3000/admin'>Подробная статистика на сайте</a>"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_admin_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.message(Command("admin"))
async def admin_command_handler(message: types.Message):
    """
    Обработчик команды /admin
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user or not user.is_registered or user.role != 'admin':
        await message.answer(
            "❌ Доступ запрещен.\n\n"
            "Эта функция доступна только администраторам."
        )
        return
    
    await message.answer(
        "🔧 <b>Админ-панель</b>\n\n"
        "Доступные команды:\n"
        "/admin_users - Список пользователей\n"
        "/admin_stats - Статистика системы\n"
        "/admin_orders - Управление заказами\n\n"
        "🌐 <a href='http://localhost:3000/admin'>Админ-панель на сайте</a>",
        parse_mode="HTML",
        disable_web_page_preview=True
    )


@router.message(Command("admin_users"))
async def admin_users_command_handler(message: types.Message):
    """
    Обработчик команды /admin_users
    """
    user_service = UserService()
    admin_service = AdminService()
    
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user or not user.is_registered or user.role != 'admin':
        await message.answer(
            "❌ Доступ запрещен.\n\n"
            "Эта функция доступна только администраторам."
        )
        return
    
    users = await admin_service.get_all_users()
    
    users_text = "👥 <b>Пользователи</b>\n\n"
    for i, u in enumerate(users[:5], 1):  # Показываем первые 5 пользователей
        users_text += (
            f"{i}. 👤 <b>{u.first_name or u.username or 'Без имени'}</b>\n"
            f"   Email: {u.email or 'Не указан'}\n"
            f"   Роль: {u.role or 'Не указана'}\n\n"
        )
    
    if len(users) > 5:
        users_text += f"... и еще {len(users) - 5} пользователей\n\n"
    
    users_text += "🌐 <a href='http://localhost:3000/admin'>Все пользователи на сайте</a>"
    
    await message.answer(
        users_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    ) 