import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..keyboards.auth_keyboards import get_auth_keyboard
from ..services.user_service import UserService

router = Router(name="auth_router")
logger = logging.getLogger(__name__)


class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()


@router.callback_query(F.data == "auth")
async def auth_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик аутентификации
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    try:
        if user and user.is_registered:
            await callback.message.edit_text(
                f"✅ Вы уже авторизованы!\n\n"
                f"Имя: {user.first_name or 'Не указано'}\n"
                f"Email: {user.email or 'Не указан'}\n"
                f"Роль: {user.role or 'Не указана'}",
                reply_markup=get_auth_keyboard()
            )
        else:
            await callback.message.edit_text(
                "🔐 <b>Авторизация</b>\n\n"
                "Для использования бота необходимо зарегистрироваться на сайте.\n\n"
                "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>\n"
                "🔗 <a href='http://localhost:3000/login'>Войти в аккаунт</a>",
                reply_markup=get_auth_keyboard(),
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    except Exception as e:
        # Если сообщение не изменилось, просто отвечаем на callback
        logger.debug(f"Message edit failed (likely unchanged): {e}")
    
    await callback.answer()


@router.callback_query(F.data == "link_account")
async def link_account_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик привязки аккаунта
    """
    try:
        await callback.message.edit_text(
            "🔗 <b>Привязка аккаунта</b>\n\n"
            "Для привязки Telegram к существующему аккаунту:\n\n"
            "1. Войдите в свой аккаунт на сайте\n"
            "2. Перейдите в настройки профиля\n"
            "3. Укажите ваш Telegram ID: <code>{}</code>\n\n"
            "🌐 <a href='http://localhost:3000/profile'>Настройки профиля</a>".format(
                callback.from_user.id
            ),
            reply_markup=get_auth_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        # Если сообщение не изменилось, просто отвечаем на callback
        logger.debug(f"Message edit failed (likely unchanged): {e}")
    
    await callback.answer()


@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    """
    Обработчик команды /profile
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if user and user.is_registered:
        profile_text = (
            f"👤 <b>Профиль</b>\n\n"
            f"Имя: {user.first_name or 'Не указано'}\n"
            f"Email: {user.email or 'Не указан'}\n"
            f"Роль: {user.role or 'Не указана'}\n"
            f"Telegram ID: {user.telegram_id}\n\n"
            f"🌐 <a href='http://localhost:3000/profile'>Редактировать профиль</a>"
        )
        await message.answer(profile_text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.answer(
            "❌ Вы не авторизованы.\n\n"
            "Для просмотра профиля необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        ) 