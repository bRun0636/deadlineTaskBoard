import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from ..keyboards.profile_keyboards import get_profile_keyboard
from ..services.user_service import UserService

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
        f"Роль: {user.role or 'Не указана'}\n"
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
async def edit_profile_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик редактирования профиля
    """
    await callback.message.edit_text(
        "✏️ <b>Редактирование профиля</b>\n\n"
        "Для редактирования профиля перейдите на сайт:\n\n"
        "🌐 <a href='http://localhost:3000/profile'>Редактировать профиль</a>\n\n"
        "Там вы сможете изменить:\n"
        "• Имя и фамилию\n"
        "• Email\n"
        "• Пароль\n"
        "• Роль\n"
        "• Другие настройки",
        reply_markup=get_profile_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
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
async def profile_command_handler(message: types.Message):
    """
    Обработчик команды /profile
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы не авторизованы.\n\n"
            "Для просмотра профиля необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return
    
    profile_text = (
        f"👤 <b>Профиль</b>\n\n"
        f"Имя: {user.first_name or 'Не указано'}\n"
        f"Email: {user.email or 'Не указан'}\n"
        f"Роль: {user.role or 'Не указана'}\n"
        f"Telegram ID: {user.telegram_id}\n"
        f"Дата регистрации: {user.created_at.strftime('%d.%m.%Y') if user.created_at else 'Неизвестно'}\n\n"
        f"🌐 <a href='http://localhost:3000/profile'>Редактировать профиль</a>"
    )
    
    await message.answer(
        profile_text,
        parse_mode="HTML",
        disable_web_page_preview=True
    ) 

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