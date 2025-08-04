from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_auth_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура для аутентификации
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🔗 Привязать аккаунт", callback_data="link_account")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 