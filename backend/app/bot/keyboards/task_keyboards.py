from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_tasks_menu_keyboard() -> InlineKeyboardMarkup:
    """
    Меню задач
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📋 Мои задачи", callback_data="my_tasks"),
            InlineKeyboardButton(text="➕ Создать задачу", callback_data="create_task")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_task_keyboard(task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для конкретной задачи
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_task:{task_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_task:{task_id}")
        ],
        [
            InlineKeyboardButton(text="📋 Все задачи", callback_data="tasks"),
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 