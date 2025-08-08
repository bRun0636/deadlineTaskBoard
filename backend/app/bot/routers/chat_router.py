import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..keyboards.chat_keyboards import get_chat_menu_keyboard, get_chat_keyboard
from ..services.chat_service import ChatService
from ..services.user_service import UserService
from app.models.user import User

router = Router(name="chat_router")
logger = logging.getLogger(__name__)


class ChatStates(StatesGroup):
    waiting_for_message = State()


@router.callback_query(F.data == "chat")
async def chat_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик меню чатов
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    
    if not user or not user.is_registered:
        await callback.message.edit_text(
            "❌ Вы не авторизованы.\n\n"
            "Для работы с чатами необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "💬 <b>Чаты</b>\n\n"
        "Выберите действие:",
        reply_markup=get_chat_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "my_chats")
async def my_chats_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик просмотра своих чатов
    """
    user_service = UserService()
    chat_service = ChatService()
    
    user = await user_service.get_user_by_telegram_id(callback.from_user.id)
    chats = await chat_service.get_user_chats(user.id)
    
    if not chats:
        await callback.message.edit_text(
            "💬 <b>Мои чаты</b>\n\n"
            "У вас пока нет активных чатов.\n\n"
            "🌐 <a href='http://localhost:3000/chat'>Чаты на сайте</a>",
            reply_markup=get_chat_menu_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    else:
        chats_text = "💬 <b>Мои чаты</b>\n\n"
        for i, chat in enumerate(chats[:10], 1):  # Показываем первые 10 чатов
            chats_text += (
                f"{i}. 💬 <b>{chat.order.title if chat.order else 'Чат'}</b>\n"
                f"   Последнее сообщение: {chat.last_message_time.strftime('%d.%m.%Y %H:%M') if chat.last_message_time else 'Нет сообщений'}\n"
                f"   Сообщений: {chat.message_count if hasattr(chat, 'message_count') else 'Неизвестно'}\n\n"
            )
        
        if len(chats) > 10:
            chats_text += f"... и еще {len(chats) - 10} чатов\n\n"
        
        chats_text += "🌐 <a href='http://localhost:3000/chat'>Все чаты на сайте</a>"
        
        await callback.message.edit_text(
            chats_text,
            reply_markup=get_chat_menu_keyboard(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    
    await callback.answer()


@router.callback_query(F.data == "new_message")
async def new_message_handler(callback: types.CallbackQuery, state: FSMContext):
    """
    Обработчик создания нового сообщения
    """
    await callback.message.edit_text(
        "💬 <b>Новое сообщение</b>\n\n"
        "Для отправки сообщения перейдите на сайт:\n\n"
        "🌐 <a href='http://localhost:3000/chat'>Отправить сообщение</a>\n\n"
        "Или используйте команду /message",
        reply_markup=get_chat_menu_keyboard(),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


@router.message(Command("chat"))
async def chat_command_handler(message: types.Message):
    """
    Обработчик команды /chat
    """
    user_service = UserService()
    chat_service = ChatService()
    
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы не авторизованы.\n\n"
            "Для работы с чатами необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return
    
    chats = await chat_service.get_user_chats(user.id)
    
    if not chats:
        await message.answer(
            "💬 <b>Мои чаты</b>\n\n"
            "У вас пока нет активных чатов.\n\n"
            "🌐 <a href='http://localhost:3000/chat'>Чаты на сайте</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    else:
        chats_text = "💬 <b>Мои чаты</b>\n\n"
        for i, chat in enumerate(chats[:5], 1):  # Показываем первые 5 чатов
            chats_text += (
                f"{i}. 💬 <b>{chat.order.title if chat.order else 'Чат'}</b>\n"
                f"   Последнее сообщение: {chat.last_message_time.strftime('%d.%m.%Y %H:%M') if chat.last_message_time else 'Нет сообщений'}\n\n"
            )
        
        if len(chats) > 5:
            chats_text += f"... и еще {len(chats) - 5} чатов\n\n"
        
        chats_text += "🌐 <a href='http://localhost:3000/chat'>Все чаты на сайте</a>"
        
        await message.answer(
            chats_text,
            parse_mode="HTML",
            disable_web_page_preview=True
        )


@router.message(Command("message"))
async def message_command_handler(message: types.Message, state: FSMContext):
    """
    Обработчик команды /message для отправки сообщения
    """
    user_service = UserService()
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы не авторизованы.\n\n"
            "Для отправки сообщений необходимо зарегистрироваться на сайте.\n"
            "🌐 <a href='http://localhost:3000/register'>Зарегистрироваться</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return
    
    # Парсим аргументы команды
    args = message.text.split()[1:]
    if len(args) < 2:
        await message.answer(
            "💬 <b>Отправка сообщения</b>\n\n"
            "Использование: /message [ID_заказа] [текст_сообщения]\n\n"
            "Пример: /message 1 Привет! Как дела с заказом?\n\n"
            "🌐 <a href='http://localhost:3000/chat'>Отправить сообщение на сайте</a>",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        return
    
    try:
        order_id = int(args[0])
        message_text = " ".join(args[1:])
        
        chat_service = ChatService()
        result = await chat_service.send_message(user.id, order_id, message_text)
        
        if result:
            await message.answer(
                f"✅ Сообщение отправлено в заказ #{order_id}\n\n"
                f"🌐 <a href='http://localhost:3000/chat/{order_id}'>Открыть чат на сайте</a>",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        else:
            await message.answer(
                f"❌ Не удалось отправить сообщение в заказ #{order_id}\n\n"
                f"Возможные причины:\n"
                f"• Заказ не найден\n"
                f"• У вас нет доступа к этому заказу\n"
                f"• Заказ не в статусе 'в работе'\n\n"
                f"🌐 <a href='http://localhost:3000/chat'>Чаты на сайте</a>",
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    
    except ValueError:
        await message.answer(
            "❌ Неверный формат команды.\n\n"
            "Использование: /message [ID_заказа] [текст_сообщения]\n\n"
            "Пример: /message 1 Привет! Как дела с заказом?",
            parse_mode="HTML"
        ) 


@router.callback_query(F.data.startswith("send_message:"))
async def send_message_handler(callback: types.CallbackQuery, user: User):
    """
    Обработчик кнопки "Отправить сообщение"
    """
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    try:
        chat_id = int(callback.data.split(":")[-1])
        
        send_text = (
            f"💬 <b>Отправка сообщения</b>\n\n"
            f"Чат ID: {chat_id}\n\n"
            f"💡 <b>Для отправки сообщения перейдите на сайт:</b>\n"
            f"🌐 <a href='http://localhost:3000/chat/{chat_id}'>Открыть чат</a>\n\n"
            f"Там вы сможете:\n"
            "• Отправить текстовое сообщение\n"
            "• Прикрепить файлы\n"
            "• Отправить изображения\n"
            "• Просмотреть историю сообщений"
        )
        
        from ..keyboards.chat_keyboards import get_chat_keyboard
        await callback.message.edit_text(
            send_text,
            reply_markup=get_chat_keyboard(chat_id),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
        
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        await callback.answer("❌ Произошла ошибка!", show_alert=True) 