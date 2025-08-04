from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_chat_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Меню чатов
    """
    keyboard = [
        [
            InlineKeyboardButton(text="💬 Мои чаты", callback_data="my_chats"),
            InlineKeyboardButton(text="✉️ Новое сообщение", callback_data="new_message")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_chat_keyboard(chat_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для конкретного чата
    """
    keyboard = [
        [
            InlineKeyboardButton(text="💬 Отправить сообщение", callback_data=f"send_message:{chat_id}")
        ],
        [
            InlineKeyboardButton(text="💬 Все чаты", callback_data="chat"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 