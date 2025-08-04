import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from ..services.user_service import UserService
from ..services.order_service import OrderService
from ..keyboards.order_keyboards import get_orders_menu_keyboard
from app.models.user import User

router = Router(name="orders_router")
logger = logging.getLogger(__name__)

@router.message(Command("orders"))
async def show_orders_menu(message: types.Message, user: User):
    """Показать меню заказов"""
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы должны быть зарегистрированы для работы с заказами.\n"
            "Используйте /register для регистрации."
        )
        return
    
    await message.answer(
        "📊 <b>Управление заказами</b>\n\n"
        "Выберите действие:",
        reply_markup=get_orders_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "orders")
async def show_orders(callback: types.CallbackQuery, user: User):
    """Показать заказы"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        order_service = OrderService()
        orders = await order_service.get_user_orders(user.id)
        
        if not orders:
            await callback.message.edit_text(
                "📊 <b>Заказы</b>\n\n"
                "У вас пока нет заказов.\n"
                "Создайте новый заказ!",
                reply_markup=get_orders_menu_keyboard(),
                parse_mode="HTML"
            )
            return
        
        # Формируем список заказов
        orders_text = "📊 <b>Ваши заказы:</b>\n\n"
        for i, order in enumerate(orders[:10], 1):  # Показываем первые 10
            status_emoji = {
                'open': '🟢',
                'in_progress': '🟡',
                'completed': '✅',
                'cancelled': '❌'
            }.get(order.status, '📝')
            
            orders_text += (
                f"{i}. {status_emoji} <b>{order.title}</b>\n"
                f"   Статус: {order.status}\n"
                f"   Бюджет: {order.budget or 'Не указан'} ₽\n"
                f"   Создан: {order.created_at.strftime('%d.%m.%Y')}\n\n"
            )
        
        if len(orders) > 10:
            orders_text += f"... и еще {len(orders) - 10} заказов"
        
        try:
            await callback.message.edit_text(
                orders_text,
                reply_markup=get_orders_menu_keyboard(),
                parse_mode="HTML"
            )
        except TelegramBadRequest as e:
            if "message is not modified" in str(e):
                # Игнорируем ошибку если сообщение не изменилось
                pass
            else:
                raise
        
    except Exception as e:
        logger.error(f"Error showing orders for user {user.id}: {e}")
        await callback.message.edit_text(
            "❌ Произошла ошибка при загрузке заказов.",
            reply_markup=get_orders_menu_keyboard()
        ) 