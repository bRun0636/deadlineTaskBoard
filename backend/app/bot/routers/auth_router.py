import logging
import httpx
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..keyboards.auth_keyboards import get_auth_keyboard
from ..services.user_service import UserService
from app.config import settings

router = Router(name="auth_router")
logger = logging.getLogger(__name__)


class RegistrationStates(StatesGroup):
    waiting_for_email = State()
    waiting_for_password = State()


class BindingStates(StatesGroup):
    waiting_for_code = State()


@router.callback_query(F.data == "auth")
async def auth_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик аутентификации
    """
    user_service = UserService()
    user = await user_service.get_or_create_user(
        telegram_id=callback.from_user.id,
        username=callback.from_user.username or f"user_{callback.from_user.id}",
        first_name=callback.from_user.first_name,
        last_name=callback.from_user.last_name
    )
    
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
        # Debug logging removed for production
        pass
    
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
            "3. Сгенерируйте код для привязки\n"
            "4. Отправьте этот код мне\n\n"
            "🌐 <a href='http://localhost:3000/profile'>Настройки профиля</a>\n\n"
            "📝 <b>Отправьте код привязки:</b>",
            reply_markup=get_auth_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
        # Устанавливаем состояние ожидания кода
        await state.set_state(BindingStates.waiting_for_code)
        
    except Exception as e:
        # Debug logging removed for production
        pass
    
    await callback.answer()


@router.message(BindingStates.waiting_for_code)
async def handle_binding_code(message: types.Message, state: FSMContext):
    """
    Обработчик кода привязки
    """
    code = message.text.strip()
    
    if not code or len(code) != 8:
        await message.answer(
            "❌ Неверный формат кода.\n\n"
            "Код должен состоять из 8 символов (буквы и цифры).\n"
            "Попробуйте еще раз или сгенерируйте новый код на сайте."
        )
        return
    
    try:
        # Отправляем запрос к API для привязки аккаунта
        url = f"{settings.api_base_url}/api/v1/telegram/bind/{code}"
        data = {
            "telegram_id": message.from_user.id,
            "telegram_username": message.from_user.username or f"user_{message.from_user.id}"
        }
        
        logger.info(f"Attempting to bind account with URL: {url}")
        logger.info(f"Data: {data}")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=data,
                timeout=10.0
            )
            
            if response.status_code == 200:
                data = response.json()
                await message.answer(
                    "✅ <b>Аккаунт успешно привязан!</b>\n\n"
                    f"Ваш аккаунт на сайте теперь связан с Telegram.\n"
                    f"Вы будете получать уведомления о новых заказах и сообщениях.\n\n"
                    "🏠 <b>Используйте главное меню для навигации</b>",
                    parse_mode="HTML"
                )
                
                # Сбрасываем состояние
                await state.clear()
                
                # Показываем главное меню
                from ..keyboards.main_keyboards import get_main_menu_keyboard
                await message.answer(
                    "🎉 <b>Добро пожаловать в Deadline Task Board!</b>\n\n"
                    "Теперь вы можете:\n"
                    "• Просматривать заказы и задачи\n"
                    "• Создавать новые проекты\n"
                    "• Общаться с другими участниками\n"
                    "• Управлять своим профилем\n\n"
                    "Выберите действие:",
                    reply_markup=get_main_menu_keyboard(is_admin=False, is_linked=True),
                    parse_mode="HTML"
                )
                
            elif response.status_code == 400:
                error_data = response.json()
                error_message = error_data.get("detail", "Неизвестная ошибка")
                
                if "истек" in error_message.lower():
                    await message.answer(
                        "❌ <b>Код привязки истек</b>\n\n"
                        "Код действителен только 10 минут.\n"
                        "Пожалуйста, сгенерируйте новый код на сайте и попробуйте снова.\n\n"
                        "🌐 <a href='http://localhost:3000/profile'>Сгенерировать новый код</a>",
                        parse_mode="HTML",
                        disable_web_page_preview=True
                    )
                elif "уже привязан" in error_message.lower():
                    await message.answer(
                        "❌ <b>Этот Telegram аккаунт уже привязан</b>\n\n"
                        "Данный Telegram аккаунт уже связан с другим пользователем.\n"
                        "Если это ваш аккаунт, обратитесь в поддержку.",
                        parse_mode="HTML"
                    )
                else:
                    await message.answer(
                        f"❌ <b>Ошибка привязки:</b> {error_message}\n\n"
                        "Попробуйте еще раз или обратитесь в поддержку.",
                        parse_mode="HTML"
                    )
                    
            elif response.status_code == 404:
                await message.answer(
                    "❌ <b>Недействительный код</b>\n\n"
                    "Код привязки не найден или уже использован.\n"
                    "Пожалуйста, сгенерируйте новый код на сайте.\n\n"
                    "🌐 <a href='http://localhost:3000/profile'>Сгенерировать новый код</a>",
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                
            else:
                await message.answer(
                    "❌ <b>Ошибка сервера</b>\n\n"
                    "Произошла ошибка при обработке запроса.\n"
                    "Попробуйте позже или обратитесь в поддержку."
                )
                
    except httpx.TimeoutException:
        await message.answer(
            "❌ <b>Превышено время ожидания</b>\n\n"
            "Сервер не отвечает. Попробуйте позже."
        )
    except Exception as e:
        logger.error(f"Error binding account: {e}")
        await message.answer(
            "❌ <b>Произошла ошибка</b>\n\n"
            "Не удалось привязать аккаунт. Попробуйте позже или обратитесь в поддержку."
        )


@router.message(Command("profile"))
async def profile_handler(message: types.Message):
    """
    Обработчик команды /profile
    """
    user_service = UserService()
    user = await user_service.get_or_create_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username or f"user_{message.from_user.id}",
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name
    )
    
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