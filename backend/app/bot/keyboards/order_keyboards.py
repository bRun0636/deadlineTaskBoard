from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


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


def get_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура действий с заказом
    """
    keyboard = [
        [
            InlineKeyboardButton(text="👁️ Просмотр", callback_data=f"view_order_{order_id}"),
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_order_{order_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Удалить", callback_data=f"delete_order_{order_id}"),
            InlineKeyboardButton(text="✅ Завершить", callback_data=f"complete_order_{order_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_orders")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения для заказов
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_order_creation"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_order_creation")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_task_confirmation_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения для задач
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_task_creation"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_task_creation")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_category_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора категории
    """
    keyboard = [
        [
            InlineKeyboardButton(text="💻 Разработка", callback_data="category_development"),
            InlineKeyboardButton(text="🎨 Дизайн", callback_data="category_design")
        ],
        [
            InlineKeyboardButton(text="📝 Копирайтинг", callback_data="category_copywriting"),
            InlineKeyboardButton(text="📱 SMM", callback_data="category_smm")
        ],
        [
            InlineKeyboardButton(text="🔍 SEO", callback_data="category_seo"),
            InlineKeyboardButton(text="📊 Аналитика", callback_data="category_analytics")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_title")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_priority_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора приоритета
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🟢 Низкий", callback_data="priority_low"),
            InlineKeyboardButton(text="🟡 Средний", callback_data="priority_medium")
        ],
        [
            InlineKeyboardButton(text="🟠 Высокий", callback_data="priority_high"),
            InlineKeyboardButton(text="🔴 Критический", callback_data="priority_critical")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_order_edit_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура редактирования заказа
    """
    keyboard = [
        [
            InlineKeyboardButton(text="📝 Название", callback_data=f"edit_title_{order_id}"),
            InlineKeyboardButton(text="📄 Описание", callback_data=f"edit_description_{order_id}")
        ],
        [
            InlineKeyboardButton(text="💰 Бюджет", callback_data=f"edit_budget_{order_id}"),
            InlineKeyboardButton(text="📅 Срок", callback_data=f"edit_deadline_{order_id}")
        ],
        [
            InlineKeyboardButton(text="🏷️ Категория", callback_data=f"edit_category_{order_id}"),
            InlineKeyboardButton(text="📋 Требования", callback_data=f"edit_requirements_{order_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к заказу", callback_data=f"view_order_{order_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard(action: str, item_id: int = None) -> InlineKeyboardMarkup:
    """
    Универсальная клавиатура подтверждения
    """
    keyboard = []
    
    if item_id:
        keyboard.append([
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{item_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{item_id}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{action}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_orders")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_proposals_keyboard(order_id: int, proposals) -> InlineKeyboardMarkup:
    """
    Клавиатура для управления предложениями к заказу
    """
    keyboard = []
    
    # Добавляем кнопки для каждого предложения (первые 5)
    for i, proposal in enumerate(proposals[:5], 1):
        executor_name = proposal.executor.full_name or proposal.executor.username or f"Исполнитель {i}"
        keyboard.append([
            InlineKeyboardButton(
                text=f"✅ Принять {executor_name[:15]}", 
                callback_data=f"accept_proposal_{order_id}_{proposal.id}"
            )
        ])
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ Отклонить {executor_name[:15]}", 
                callback_data=f"reject_proposal_{order_id}_{proposal.id}"
            )
        ])
    
    # Если предложений больше 5, добавляем кнопку "Показать еще"
    if len(proposals) > 5:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📄 Показать еще ({len(proposals) - 5})", 
                callback_data=f"show_more_proposals_{order_id}_5"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к заказам", callback_data="back_to_orders")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_order_view_keyboard(order_id: int, can_edit: bool = True) -> InlineKeyboardMarkup:
    """
    Клавиатура просмотра заказа
    """
    keyboard = []
    
    if can_edit:
        keyboard.extend([
            [
                InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_order_{order_id}"),
                InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_order_{order_id}")
            ],
            [
                InlineKeyboardButton(text="✅ Завершить", callback_data=f"complete_order_{order_id}"),
                InlineKeyboardButton(text="💼 Предложения", callback_data=f"order_proposals_{order_id}")
            ]
        ])
    else:
        keyboard.append([
            InlineKeyboardButton(text="💼 Предложения", callback_data=f"order_proposals_{order_id}")
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад к заказам", callback_data="back_to_orders")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 