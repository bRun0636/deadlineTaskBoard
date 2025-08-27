#!/usr/bin/env python3
"""
Утилиты для работы с сообщениями
"""
import logging
from aiogram import types
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)

async def safe_edit_message(message: types.Message, text: str, reply_markup=None, parse_mode="HTML"):
    """
    Безопасное редактирование сообщения с обработкой ошибок
    
    Args:
        message: Сообщение для редактирования
        text: Новый текст сообщения
        reply_markup: Новая клавиатура (опционально)
        parse_mode: Режим парсинга (по умолчанию HTML)
    
    Returns:
        bool: True если редактирование прошло успешно, False в противном случае
    """
    try:
        await message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return True
    except TelegramBadRequest as e:
        if "message is not modified" in str(e):
            # Игнорируем ошибку если сообщение не изменилось
            logger.debug("Message was not modified")
            return True
        else:
            logger.error(f"Telegram error while editing message: {e}")
            return False
    except Exception as e:
        logger.error(f"Unexpected error while editing message: {e}")
        return False

async def safe_send_message(bot, chat_id: int, text: str, reply_markup=None, parse_mode="HTML"):
    """
    Безопасная отправка сообщения с обработкой ошибок
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата для отправки
        text: Текст сообщения
        reply_markup: Клавиатура (опционально)
        parse_mode: Режим парсинга (по умолчанию HTML)
    
    Returns:
        types.Message or None: Отправленное сообщение или None при ошибке
    """
    try:
        message = await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode
        )
        return message
    except Exception as e:
        logger.error(f"Error sending message to {chat_id}: {e}")
        return None

async def safe_answer_callback(callback: types.CallbackQuery, text: str = None, show_alert: bool = False):
    """
    Безопасный ответ на callback query
    
    Args:
        callback: Callback query для ответа
        text: Текст ответа (опционально)
        show_alert: Показывать ли alert (по умолчанию False)
    
    Returns:
        bool: True если ответ прошел успешно, False в противном случае
    """
    try:
        await callback.answer(text=text, show_alert=show_alert)
        return True
    except Exception as e:
        logger.error(f"Error answering callback: {e}")
        return False
