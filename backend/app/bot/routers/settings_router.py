import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..keyboards.main_keyboards import get_settings_menu_keyboard
from ..keyboards.profile_keyboards import get_profile_edit_keyboard
from app.models.user import User, UserRole
from ..utils.message_utils import safe_edit_message

router = Router(name="settings_router")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "settings")
async def settings_menu_handler(callback: types.CallbackQuery, user: User):
    """Показать меню настроек"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = (
        "⚙️ <b>Настройки</b>\n\n"
        "🔔 <b>Уведомления</b> - настройка уведомлений\n"
        "🌍 <b>Язык</b> - выбор языка интерфейса\n"
        "🔒 <b>Приватность</b> - настройки приватности\n"
        "💰 <b>Платежи</b> - способы оплаты\n"
        "📱 <b>Telegram</b> - настройки Telegram\n\n"
        "Выберите раздел для настройки:"
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "notification_settings")
async def notification_settings_handler(callback: types.CallbackQuery, user: User):
    """Настройки уведомлений"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = (
        "🔔 <b>Настройки уведомлений</b>\n\n"
        "📧 <b>Email уведомления:</b>\n"
        "• Новые заказы: ✅ Включены\n"
        "• Сообщения: ✅ Включены\n"
        "• Системные: ✅ Включены\n"
        "• Реклама: ❌ Отключены\n\n"
        "📱 <b>Telegram уведомления:</b>\n"
        "• Новые заказы: ✅ Включены\n"
        "• Сообщения: ✅ Включены\n"
        "• Системные: ✅ Включены\n"
        "• Реклама: ❌ Отключены\n\n"
        "💡 <b>Частота уведомлений:</b>\n"
        "• Мгновенно: ✅\n"
        "• Раз в час: ❌\n"
        "• Раз в день: ❌"
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "language_settings")
async def language_settings_handler(callback: types.CallbackQuery, user: User):
    """Настройки языка"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = (
        "🌍 <b>Настройки языка</b>\n\n"
        "🇷🇺 <b>Текущий язык:</b> Русский\n\n"
        "📝 <b>Доступные языки:</b>\n"
        "• 🇷🇺 Русский - ✅ Активен\n"
        "• 🇺🇸 English - ❌ Недоступен\n"
        "• 🇨🇳 中文 - ❌ Недоступен\n"
        "• 🇪🇸 Español - ❌ Недоступен\n\n"
        "💡 <b>Примечание:</b>\n"
        "В данный момент доступен только русский язык.\n"
        "Другие языки будут добавлены в ближайшее время."
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "privacy_settings")
async def privacy_settings_handler(callback: types.CallbackQuery, user: User):
    """Настройки приватности"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = (
        "🔒 <b>Настройки приватности</b>\n\n"
        "👤 <b>Видимость профиля:</b>\n"
        "• Имя и фамилия: ✅ Публично\n"
        "• Email: ❌ Только для заказчиков\n"
        "• Телефон: ❌ Приватно\n"
        "• Рейтинг: ✅ Публично\n"
        "• Навыки: ✅ Публично\n\n"
        "📊 <b>Статистика:</b>\n"
        "• Выполненные задачи: ✅ Публично\n"
        "• Заработок: ❌ Приватно\n"
        "• Отзывы: ✅ Публично\n\n"
        "💡 <b>Управление:</b>\n"
        "Для изменения настроек приватности обратитесь в поддержку."
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "payment_settings")
async def payment_settings_handler(callback: types.CallbackQuery, user: User):
    """Настройки платежей"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = (
        "💰 <b>Настройки платежей</b>\n\n"
        "💳 <b>Способы оплаты:</b>\n"
        "• Банковская карта: ✅ Настроена\n"
        "• Электронные кошельки: ❌ Не настроено\n"
        "• Криптовалюта: ❌ Не настроено\n\n"
        "📊 <b>Статистика:</b>\n"
        f"• Общий заработок: {user.total_earnings or 0} ₽\n"
        "• Выполнено сделок: 0\n"
        "• Средняя оценка: 0.0\n\n"
        "💡 <b>Добавить способ оплаты:</b>\n"
        "Для добавления новых способов оплаты обратитесь в поддержку."
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "telegram_settings")
async def telegram_settings_handler(callback: types.CallbackQuery, user: User):
    """Настройки Telegram"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = (
        "📱 <b>Настройки Telegram</b>\n\n"
        f"🆔 <b>Telegram ID:</b> {user.telegram_id}\n"
        f"👤 <b>Username:</b> @{user.telegram_username or 'Не указан'}\n"
        f"🔗 <b>Привязка:</b> ✅ Активна\n\n"
        "🔔 <b>Уведомления:</b>\n"
        "• Новые заказы: ✅ Включены\n"
        "• Сообщения: ✅ Включены\n"
        "• Системные: ✅ Включены\n"
        "• Реклама: ❌ Отключены\n\n"
        "💡 <b>Управление:</b>\n"
        "Для изменения настроек Telegram обратитесь в поддержку."
    )
    
    await callback.message.edit_text(
        settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()

