from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_orders_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Меню заказов
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📦 Мои заказы", callback_data="my_orders"),
            InlineKeyboardButton(text="🔍 Доступные заказы", callback_data="available_orders")
        ],
        [
            InlineKeyboardButton(text="➕ Создать заказ", callback_data="create_order")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 