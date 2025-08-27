import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from ..keyboards.main_keyboards import (
    get_main_menu_keyboard, get_messages_menu_keyboard
)
from ..services.user_service import UserService
from ..services.chat_service import ChatService
from app.models.user import User

router = Router(name="chat_router")
logger = logging.getLogger(__name__)

@router.message(Command("chat"))
async def show_chat_menu(message: types.Message, user: User):
    """Показать меню чатов"""
    if not user or not user.is_registered:
        await message.answer(
            "❌ Вы должны быть зарегистрированы для работы с чатами.\n"
            "Используйте /register для регистрации."
        )
        return
    
    await message.answer(
        "💬 <b>Управление сообщениями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_messages_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "messages")
async def show_messages_menu_handler(callback: types.CallbackQuery, user: User):
    """Показать меню сообщений"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "💬 <b>Управление сообщениями</b>\n\n"
        "Выберите действие:",
        reply_markup=get_messages_menu_keyboard(),
        parse_mode="HTML"
    )

@router.callback_query(F.data == "my_chats")
async def show_my_chats(callback: types.CallbackQuery, user: User):
    """Показать мои чаты"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Получаем реальные чаты пользователя
    from ..services.chat_service import ChatService
    chat_service = ChatService()
    chats = await chat_service.get_user_chats(user.id)
    
    if not chats:
        chats_text = "💬 <b>Мои чаты:</b>\n\n"
        chats_text += "📭 У вас пока нет активных чатов.\n\n"
        chats_text += "💡 <b>Как начать общение:</b>\n"
        chats_text += "• Создайте заказ и дождитесь предложений\n"
        chats_text += "• Отправьте предложение на существующий заказ\n"
        chats_text += "• После принятия предложения чат станет доступен\n\n"
        chats_text += "🌐 <a href='http://localhost:3000/orders'>Перейти к заказам</a>"
    else:
        chats_text = "💬 <b>Мои чаты:</b>\n\n"
        for i, chat in enumerate(chats[:10], 1):  # Показываем первые 10 чатов
            chats_text += f"{i}. <b>{chat.get('order_title', 'Без названия')}</b>\n"
            participants = chat.get('participants', [])
            chats_text += f"   Участники: {len(participants)} чел.\n"
            if chat.get('last_message_time'):
                chats_text += f"   Последнее сообщение: {chat['last_message_time'].strftime('%d.%m.%Y %H:%M')}\n"
            chats_text += "\n"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=chats_text,
        reply_markup=get_messages_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "new_messages")
async def show_new_messages(callback: types.CallbackQuery, user: User):
    """Показать новые сообщения"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Получаем реальные новые сообщения пользователя
    from ..services.chat_service import ChatService
    chat_service = ChatService()
    new_messages = await chat_service.get_new_messages(user.id)
    
    if not new_messages:
        messages_text = "📨 <b>Новые сообщения:</b>\n\n"
        messages_text += "📭 У вас нет новых сообщений.\n\n"
        messages_text += "💡 <b>Сообщения появятся когда:</b>\n"
        messages_text += "• Кто-то ответит на ваш заказ\n"
        messages_text += "• Заказчик примет ваше предложение\n"
        messages_text += "• Начнется обсуждение по заказу\n\n"
        messages_text += "🌐 <a href='http://localhost:3000/orders'>Перейти к заказам</a>"
    else:
        messages_text = "📨 <b>Новые сообщения:</b>\n\n"
        for i, msg in enumerate(new_messages[:10], 1):  # Показываем первые 10 сообщений
            sender_name = msg.sender.display_name if msg.sender else 'Неизвестно'
            messages_text += f"{i}. <b>От: {sender_name}</b>\n"
            messages_text += f"   {msg.content[:50]}{'...' if len(msg.content) > 50 else ''}\n"
            messages_text += f"   {msg.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=messages_text,
        reply_markup=get_messages_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "send_message")
async def send_message_handler(callback: types.CallbackQuery, user: User):
    """Обработчик отправки сообщения"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Показываем инструкцию по отправке сообщений
    message_text = (
        "📤 <b>Отправка сообщения</b>\n\n"
        "💡 <b>Как отправить сообщение:</b>\n"
        "1. Найдите заказ, по которому хотите общаться\n"
        "2. Нажмите на заказ, чтобы открыть его\n"
        "3. В разделе чата напишите ваше сообщение\n"
        "4. Нажмите кнопку 'Отправить'\n\n"
        "📋 <b>Доступные чаты:</b>\n"
        "• Заказы, где вы заказчик\n"
        "• Заказы, где вы исполнитель\n"
        "• Заказы в статусе 'В работе' или 'Завершен'\n\n"
        "🌐 <b>Также доступно на сайте:</b>\n"
        "Используйте веб-версию для более удобного общения."
    )
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=message_text,
        reply_markup=get_messages_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True)

@router.callback_query(F.data == "message_history")
async def show_message_history(callback: types.CallbackQuery, user: User):
    """Показать историю сообщений"""
    if not user or not user.is_registered:
        await callback.answer("❌ Вы должны быть зарегистрированы!", show_alert=True)
        return
    
    # Получаем реальную историю сообщений пользователя
    from ..services.chat_service import ChatService
    chat_service = ChatService()
    message_history = await chat_service.get_message_history(user.id)
    
    if not message_history:
        messages_text = "📋 <b>История сообщений:</b>\n\n"
        messages_text += "📭 У вас пока нет сообщений.\n\n"
        messages_text += "💡 <b>Сообщения появятся когда:</b>\n"
        messages_text += "• Вы начнете общение по заказу\n"
        messages_text += "• Кто-то ответит на ваше сообщение\n"
        messages_text += "• Заказчик и исполнитель начнут обсуждение\n\n"
        messages_text += "🌐 <a href='http://localhost:3000/orders'>Перейти к заказам</a>"
    else:
        messages_text = "📋 <b>История сообщений:</b>\n\n"
        for i, msg in enumerate(message_history[:15], 1):  # Показываем последние 15 сообщений
            direction = "📤 Отправлено" if msg.sender_id == user.id else "📥 Получено"
            sender_name = msg.sender.display_name if msg.sender else 'Неизвестно'
            messages_text += f"{i}. {direction} <b>{sender_name}</b>\n"
            messages_text += f"   {msg.content[:60]}{'...' if len(msg.content) > 60 else ''}\n"
            messages_text += f"   {msg.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
    
    from ..utils.message_utils import safe_edit_message
    
    success = await safe_edit_message(
        message=callback.message,
        text=messages_text,
        reply_markup=get_messages_menu_keyboard(),
        parse_mode="HTML"
    )
    
    if not success:
        await callback.answer("❌ Произошла ошибка при обновлении сообщения", show_alert=True) 