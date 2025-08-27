import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from ..keyboards.main_keyboards import (
    get_main_menu_keyboard, get_profile_keyboard,
    get_rating_menu_keyboard, get_settings_menu_keyboard
)
from ..services.user_service import UserService
from app.models.user import User, UserRole

def get_role_display_name(role):
    """Преобразует роль в понятное название"""
    role_mapping = {
        UserRole.ADMIN: "👨‍💼 Администратор",
        UserRole.CUSTOMER: "👤 Заказчик", 
        UserRole.EXECUTOR: "👨‍💻 Исполнитель"
    }
    return role_mapping.get(role, str(role))

router = Router(name="profile_router")
logger = logging.getLogger(__name__)


@router.callback_query(F.data == "profile")
async def profile_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик меню профиля
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_registered:
        await callback.message.edit_text(
            "❌ Вы не авторизованы.\n\n"
            "Для просмотра профиля необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await callback.answer()
        return
    
    profile_text = (
        f"👤 <b>Профиль</b>\n\n"
        f"Имя: {user.first_name or 'Не указано'}\n"
        f"Email: {user.email or 'Не указан'}\n"
        f"Роль: {get_role_display_name(user.role) or 'Не указана'}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y') if user.created_at else 'Неизвестно'}\n\n"
        f"🌐 <a href='http://localhost:3000/profile'>Редактировать профиль</a>"
    )
    
    await callback.message.edit_text(
        profile_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.callback_query(F.data == "edit_profile")
async def edit_profile_handler(callback: types.CallbackQuery, user: User):
    """Редактирование профиля"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    edit_text = (
        "✏️ <b>Редактирование профиля</b>\n\n"
        f"👤 <b>Имя:</b> {user.first_name or 'Не указано'}\n"
        f"📝 <b>Фамилия:</b> {user.last_name or 'Не указано'}\n"
        f"📧 <b>Email:</b> {user.email or 'Не указан'}\n"
        f"📱 <b>Телефон:</b> {user.phone or 'Не указан'}\n"
        f"🌍 <b>Страна:</b> {user.country or 'Не указана'}\n"
        f"💼 <b>Тип:</b> {user.juridical_type or 'Не указан'}\n"
        f"📊 <b>Уровень:</b> {user.prof_level or 'Не указан'}\n\n"
        "Выберите, что хотите изменить:"
    )
    
    from ..keyboards.profile_keyboards import get_profile_edit_keyboard
    await callback.message.edit_text(
        edit_text,
        reply_markup=get_profile_edit_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "statistics")
async def statistics_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик статистики пользователя
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_registered:
        await callback.message.edit_text(
            "❌ Вы не авторизованы.\n\n"
            "Для просмотра статистики необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await callback.answer()
        return
    
    # Получаем статистику пользователя
    stats = await user_service.get_user_statistics(user.id)
    
    stats_text = (
        f"📊 <b>Статистика</b>\n\n"
        f"Созданных задач: {stats.get('tasks_created', 0)}\n"
        f"Выполненных задач: {stats.get('tasks_completed', 0)}\n"
        f"Созданных заказов: {stats.get('orders_created', 0)}\n"
        f"Выполненных заказов: {stats.get('orders_completed', 0)}\n"
        f"Отправленных сообщений: {stats.get('messages_sent', 0)}\n"
        f"Полученных предложений: {stats.get('proposals_received', 0)}\n\n"
        f"🌐 <a href='http://localhost:3000/dashboard'>Подробная статистика на сайте</a>"
    )
    
    await callback.message.edit_text(
        stats_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.message(Command("profile"))
async def show_profile_menu(message: types.Message, user: User):
    """Показать меню профиля"""
    if not user:
        await message.answer(
            "❌ Ошибка: пользователь не найден.\n"
            "Попробуйте отправить /start"
        )
        return
    
    if not user.is_registered:
        # Показываем базовую информацию для незарегистрированных пользователей
        profile_text = (
            "👤 <b>Ваш базовый профиль</b>\n\n"
            f"📝 <b>Имя:</b> {user.first_name or user.username or 'Не указано'}\n"
            f"🆔 <b>Telegram ID:</b> {user.telegram_id}\n"
            f"📅 <b>Дата создания:</b> {user.created_at.strftime('%d.%m.%Y')}\n"
            f"🎭 <b>Роль:</b> {get_role_display_name(user.role)}\n"
            f"✅ <b>Статус:</b> Не зарегистрирован\n\n"
            "💡 <b>Для полного доступа к функциям:</b>\n"
            "• Отправьте <code>/register</code> для регистрации\n"
            "• Заполните профиль с навыками и опытом\n"
            "• Выберите роль: заказчик или исполнитель\n\n"
            "🚀 <b>Что вы можете делать сейчас:</b>\n"
            "• <code>/help</code> - получить справку\n"
            "• <code>/guide</code> - изучить руководство\n"
            "• <code>/quickstart</code> - быстрый старт\n"
            "• <code>/me</code> - добавить резюме\n\n"
            "🌐 <b>Также доступна веб-версия:</b>\n"
            "<a href='http://localhost:3000'>Открыть сайт</a>"
        )
        
        await message.answer(
            profile_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return
    
    await message.answer(
        "👤 <b>Управление профилем</b>\n\n"
        "Выберите действие:",
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "profile")
async def show_profile_handler(callback: types.CallbackQuery, user: User):
    """Показать профиль пользователя"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Формируем информацию о профиле
    profile_text = "👤 <b>Ваш профиль</b>\n\n"
    profile_text += f"📝 <b>Имя:</b> {user.first_name or user.username or 'Не указано'}\n"
    profile_text += f"📧 <b>Email:</b> {user.email or 'Не указан'}\n"
    profile_text += f"🎭 <b>Роль:</b> {get_role_display_name(user.role)}\n"
    profile_text += f"🆔 <b>Telegram ID:</b> {user.telegram_id}\n"
    profile_text += f"📅 <b>Дата регистрации:</b> {user.created_at.strftime('%d.%m.%Y')}\n"
    
    if user.rating:
        profile_text += f"⭐ <b>Рейтинг:</b> {user.rating}\n"
    if user.completed_tasks:
        profile_text += f"✅ <b>Выполнено задач:</b> {user.completed_tasks}\n"
    if user.total_earnings:
        profile_text += f"💰 <b>Общий заработок:</b> {user.total_earnings} ₽\n"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=profile_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "rating")
async def show_rating_menu_handler(callback: types.CallbackQuery, user: User):
    """Показать меню рейтинга"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⭐ <b>Управление рейтингом</b>\n\n"
        "Выберите действие:",
        reply_markup=get_rating_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "my_rating")
async def show_my_rating(callback: types.CallbackQuery, user: User):
    """Показать мой рейтинг"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    rating_text = "⭐ <b>Мой рейтинг</b>\n\n"
    rating_text += f"🎯 <b>Текущий рейтинг:</b> {user.rating or 0.0}\n"
    rating_text += f"✅ <b>Выполнено задач:</b> {user.completed_tasks or 0}\n"
    rating_text += f"💰 <b>Общий заработок:</b> {user.total_earnings or 0} ₽\n"
    rating_text += f"📅 <b>В системе с:</b> {user.created_at.strftime('%d.%m.%Y')}\n\n"
    
    # Определяем уровень пользователя
    if user.rating and user.rating >= 4.5:
        level = "🏆 Эксперт"
    elif user.rating and user.rating >= 4.0:
        level = "⭐ Профессионал"
    elif user.rating and user.rating >= 3.5:
        level = "👨‍💼 Опытный"
    elif user.rating and user.rating >= 3.0:
        level = "👨‍💻 Начинающий"
    else:
        level = "🌱 Новичок"
    
    rating_text += f"🎖️ <b>Уровень:</b> {level}"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=rating_text,
        reply_markup=get_rating_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "top_executors")
async def show_top_executors(callback: types.CallbackQuery, user: User):
    """Показать топ исполнителей"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Получаем реальные данные топ исполнителей
    from ..services.user_service import UserService
    user_service = UserService()
    top_executors = await user_service.get_top_executors(10)
    
    if not top_executors:
        executors_text = "🏆 <b>Топ исполнителей:</b>\n\n"
        executors_text += "📭 Пока нет данных о исполнителях.\n"
        executors_text += "Рейтинги появятся, когда исполнители начнут выполнять задачи."
    else:
        executors_text = "🏆 <b>Топ исполнителей:</b>\n\n"
        for i, executor in enumerate(top_executors, 1):
            rating = executor.rating or 0.0
            completed_tasks = executor.completed_tasks or 0
            
            executors_text += f"{i}. <b>{executor.display_name}</b>\n"
            executors_text += f"   ⭐ Рейтинг: {rating:.1f}\n"
            executors_text += f"   ✅ Задач: {completed_tasks}\n\n"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=executors_text,
        reply_markup=get_rating_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "top_customers")
async def show_top_customers(callback: types.CallbackQuery, user: User):
    """Показать топ заказчиков"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        # Получаем реальные данные из базы
        from ..services.user_service import UserService
        user_service = UserService()
        
        # Получаем топ заказчиков по количеству заказов
        from app.database import get_db
        from app.models.user import User
        from app.models.order import Order
        from sqlalchemy import func
        
        db = next(get_db())
        
        # Запрос для получения топ заказчиков
        top_customers = db.query(
            User,
            func.count(Order.id).label('order_count'),
            func.avg(User.rating).label('avg_rating')
        ).join(Order, User.id == Order.creator_id)\
         .filter(User.role == 'customer')\
         .group_by(User.id)\
         .order_by(func.count(Order.id).desc())\
         .limit(10)\
         .all()
        
        if not top_customers:
            customers_text = "📊 <b>Рейтинг заказчиков:</b>\n\n"
            customers_text += "📭 Пока нет данных о заказчиках.\n"
            customers_text += "Заказы появятся, когда пользователи их создадут."
        else:
            customers_text = "📊 <b>Рейтинг заказчиков:</b>\n\n"
            
            for i, (customer, order_count, avg_rating) in enumerate(top_customers, 1):
                # Форматируем рейтинг
                rating_text = f"{avg_rating:.1f}" if avg_rating else "0.0"
                
                customers_text += f"{i}. <b>{customer.display_name}</b>\n"
                customers_text += f"   ⭐ Рейтинг: {rating_text}\n"
                customers_text += f"   📦 Заказов: {order_count}\n\n"
        
        db.close()
        
        from ..utils.message_utils import safe_edit_message
        
        success = await safe_edit_message(
            message=callback.message,
            text=customers_text,
            reply_markup=get_rating_menu_keyboard(),
            parse_mode="HTML"
        )
        
        if not success:
            await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)
            
    except Exception as e:
        logger.error(f"Error showing top customers: {e}")
        await callback.answer("❌ Ошибка при получении данных", show_alert=True)

@router.callback_query(F.data == "my_statistics")
async def show_my_statistics(callback: types.CallbackQuery, user: User):
    """Показать мою статистику"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    stats_text = "📈 <b>Моя статистика</b>\n\n"
    stats_text += f"👤 <b>Профиль:</b>\n"
    stats_text += f"   • Имя: {user.first_name or user.username}\n"
    stats_text += f"   • Роль: {get_role_display_name(user.role)}\n"
    stats_text += f"   • В системе: {user.created_at.strftime('%d.%m.%Y')}\n\n"
    
    stats_text += f"📊 <b>Активность:</b>\n"
    stats_text += f"   • Рейтинг: {user.rating or 0.0}\n"
    stats_text += f"   • Выполнено задач: {user.completed_tasks or 0}\n"
    stats_text += f"   • Общий заработок: {user.total_earnings or 0} ₽\n"
    stats_text += f"   • Последняя активность: {user.last_activity.strftime('%d.%m.%Y %H:%M') if user.last_activity else 'Неизвестно'}\n"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=stats_text,
        reply_markup=get_rating_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "settings")
async def show_settings_menu_handler(callback: types.CallbackQuery, user: User):
    """Показать меню настроек"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "⚙️ <b>Настройки</b>\n\n"
        "Выберите раздел настроек:",
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "notification_settings")
async def show_notification_settings(callback: types.CallbackQuery, user: User):
    """Показать настройки уведомлений"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = "🔔 <b>Настройки уведомлений</b>\n\n"
    settings_text += "📱 <b>Telegram уведомления:</b> ✅ Включены\n"
    settings_text += "📧 <b>Email уведомления:</b> ❌ Отключены\n"
    settings_text += "📲 <b>Push уведомления:</b> ❌ Отключены\n\n"
    settings_text += "💡 <b>Что вы получаете:</b>\n"
    settings_text += "• Новые заказы в вашей категории\n"
    settings_text += "• Сообщения от заказчиков/исполнителей\n"
    settings_text += "• Обновления статуса задач\n"
    settings_text += "• Системные уведомления"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "language_settings")
async def show_language_settings(callback: types.CallbackQuery, user: User):
    """Показать настройки языка"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = "🌍 <b>Настройки языка</b>\n\n"
    settings_text += "🇷🇺 <b>Текущий язык:</b> Русский\n\n"
    settings_text += "📝 <b>Доступные языки:</b>\n"
    settings_text += "• 🇷🇺 Русский (по умолчанию)\n"
    settings_text += "• 🇺🇸 English (в разработке)\n"
    settings_text += "• 🇪🇸 Español (в разработке)\n"
    settings_text += "• 🇨🇳 中文 (в разработке)"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "privacy_settings")
async def show_privacy_settings(callback: types.CallbackQuery, user: User):
    """Показать настройки приватности"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = "🔒 <b>Настройки приватности</b>\n\n"
    settings_text += "👤 <b>Профиль:</b>\n"
    settings_text += "• Показывать имя: ✅ Да\n"
    settings_text += "• Показывать email: ❌ Нет\n"
    settings_text += "• Показывать телефон: ❌ Нет\n\n"
    settings_text += "📊 <b>Активность:</b>\n"
    settings_text += "• Показывать рейтинг: ✅ Да\n"
    settings_text += "• Показывать статистику: ✅ Да\n"
    settings_text += "• Показывать онлайн статус: ❌ Нет"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "payment_settings")
async def show_payment_settings(callback: types.CallbackQuery, user: User):
    """Показать настройки платежей"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = "💰 <b>Настройки платежей</b>\n\n"
    settings_text += "💳 <b>Способы оплаты:</b>\n"
    settings_text += "• Банковская карта: ✅ Настроена\n"
    settings_text += "• Электронные кошельки: ❌ Не настроено\n"
    settings_text += "• Криптовалюта: ❌ Не настроено\n\n"
    settings_text += "📊 <b>Статистика:</b>\n"
    settings_text += f"• Общий заработок: {user.total_earnings or 0} ₽\n"
    settings_text += "• Выполнено сделок: 0\n"
    settings_text += "• Средняя оценка: 0.0"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "telegram_settings")
async def show_telegram_settings(callback: types.CallbackQuery, user: User):
    """Показать настройки Telegram"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    settings_text = "📱 <b>Настройки Telegram</b>\n\n"
    settings_text += f"🆔 <b>Telegram ID:</b> {user.telegram_id}\n"
    settings_text += f"👤 <b>Username:</b> @{user.telegram_username or 'Не указан'}\n"
    settings_text += f"🔗 <b>Привязка:</b> ✅ Активна\n\n"
    settings_text += "🔔 <b>Уведомления:</b>\n"
    settings_text += "• Новые заказы: ✅ Включены\n"
    settings_text += "• Сообщения: ✅ Включены\n"
    settings_text += "• Системные: ✅ Включены\n"
    settings_text += "• Реклама: ❌ Отключены"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=settings_text,
        reply_markup=get_settings_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "my_reviews")
async def my_reviews_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик кнопки "Мои отзывы"
    """
    reviews_text = (
        "⭐ <b>Мои отзывы</b>\n\n"
        "📝 <b>Полученные отзывы:</b>\n"
        "• От @alex_dev: \"Отличная работа! Быстро и качественно\" ⭐⭐⭐⭐⭐\n"
        "• От @maria_design: \"Профессиональный подход\" ⭐⭐⭐⭐⭐\n"
        "• От @ivan_copy: \"Спасибо за сотрудничество\" ⭐⭐⭐⭐\n\n"
        "📝 <b>Оставленные отзывы:</b>\n"
        "• Для @dmitry_web: \"Хороший исполнитель\" ⭐⭐⭐⭐⭐\n"
        "• Для @elena_ui: \"Рекомендую\" ⭐⭐⭐⭐\n\n"
        "📊 <b>Статистика отзывов:</b>\n"
        "• Средний рейтинг: 4.6 ⭐\n"
        "• Всего отзывов: 8\n"
        "• Положительных: 7\n"
        "• Нейтральных: 1\n"
        "• Отрицательных: 0\n\n"
        "💡 <b>Как получить больше отзывов:</b>\n"
        "• Выполняйте работу качественно\n"
        "• Соблюдайте дедлайны\n"
        "• Общайтесь с заказчиками\n"
        "• Просите оставить отзыв после завершения\n\n"
        "🌐 <a href='http://localhost:3000/profile/reviews'>Подробнее на сайте</a>"
    )
    
    await callback.message.edit_text(
        reviews_text,
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer() 