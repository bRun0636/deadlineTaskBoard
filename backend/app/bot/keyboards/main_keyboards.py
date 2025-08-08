from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard(is_admin: bool = False, is_linked: bool = True) -> InlineKeyboardMarkup:
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Мои задачи", callback_data="my_tasks")
    builder.button(text="📝 Создать задачу", callback_data="create_task")
    builder.button(text="📊 Заказы", callback_data="orders")
    builder.button(text="➕ Создать заказ", callback_data="create_order")
    builder.button(text="👤 Профиль", callback_data="profile")
    builder.button(text="⭐ Рейтинг", callback_data="rating")
    builder.button(text="💬 Сообщения", callback_data="messages")
    builder.button(text="⚙️ Настройки", callback_data="settings")

    # Добавляем кнопку привязки аккаунта для непривязанных пользователей
    if not is_linked:
        builder.button(text="🔗 Привязать аккаунт", callback_data="link_account")

    # Добавляем кнопку админ-панели только для администраторов
    if is_admin:
        builder.button(text="🔧 Админ-панель", callback_data="admin")

    builder.adjust(2)
    return builder.as_markup()

def get_task_actions_keyboard(task_id: int = None) -> InlineKeyboardMarkup:
    """Действия с задачей"""
    builder = InlineKeyboardBuilder()
    if task_id:
        builder.button(text="✏️ Редактировать", callback_data=f"edit_task_{task_id}")
        builder.button(text="🗑️ Удалить", callback_data=f"delete_task_{task_id}")
        builder.button(text="✅ Завершить", callback_data=f"complete_task_{task_id}")
        builder.button(text="👤 Назначить", callback_data=f"assign_task_{task_id}")
        builder.button(text="🔙 Назад", callback_data="back_to_tasks")
    else:
        builder.button(text="📋 Мои задачи", callback_data="my_tasks")
        builder.button(text="📝 Создать задачу", callback_data="create_task")
        builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(2, 1)
    return builder.as_markup()

def get_order_actions_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Действия с заказом"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Редактировать", callback_data=f"edit_order_{order_id}")
    builder.button(text="🗑️ Удалить", callback_data=f"delete_order_{order_id}")
    builder.button(text="✅ Завершить", callback_data=f"complete_order_{order_id}")
    builder.button(text="💼 Предложения", callback_data=f"order_proposals_{order_id}")
    builder.button(text="🔙 Назад", callback_data="back_to_orders")
    builder.adjust(2)
    return builder.as_markup()

def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Меню профиля"""
    builder = InlineKeyboardBuilder()
    builder.button(text="✏️ Редактировать профиль", callback_data="edit_profile")
    builder.button(text="📊 Статистика", callback_data="statistics")
    builder.button(text="⭐ Мои отзывы", callback_data="my_reviews")
    builder.button(text="🔗 Привязать аккаунт", callback_data="link_account")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_settings_keyboard() -> InlineKeyboardMarkup:
    """Настройки"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔔 Уведомления", callback_data="notification_settings")
    builder.button(text="🌍 Язык", callback_data="language_settings")
    builder.button(text="🔒 Приватность", callback_data="privacy_settings")
    builder.button(text="🔙 Назад", callback_data="back_to_main")
    builder.adjust(1)
    return builder.as_markup()

def get_priority_keyboard() -> InlineKeyboardMarkup:
    """Выбор приоритета"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🟢 Низкий (1)", callback_data="priority_1")
    builder.button(text="🟡 Средний (2)", callback_data="priority_2")
    builder.button(text="🟠 Высокий (3)", callback_data="priority_3")
    builder.button(text="🔴 Критический (4)", callback_data="priority_4")
    builder.adjust(2)
    return builder.as_markup()

def get_confirmation_keyboard(action: str, item_id: int = None) -> InlineKeyboardMarkup:
    """Подтверждение действия"""
    builder = InlineKeyboardBuilder()
    if item_id:
        builder.button(text="✅ Да", callback_data=f"confirm_{action}_{item_id}")
        builder.button(text="❌ Нет", callback_data=f"cancel_{action}_{item_id}")
    else:
        builder.button(text="✅ Подтвердить", callback_data=f"confirm_{action}")
        builder.button(text="❌ Отменить", callback_data=f"cancel_{action}")
    builder.adjust(2)
    return builder.as_markup()

def get_pagination_keyboard(page: int, total_pages: int, action: str) -> InlineKeyboardMarkup:
    """Пагинация"""
    builder = InlineKeyboardBuilder()
    
    if page > 1:
        builder.button(text="⬅️", callback_data=f"{action}_page_{page-1}")
    
    builder.button(text=f"{page}/{total_pages}", callback_data="current_page")
    
    if page < total_pages:
        builder.button(text="➡️", callback_data=f"{action}_page_{page+1}")
    
    builder.button(text="🔙 Назад", callback_data=f"back_to_{action}")
    builder.adjust(3, 1)
    return builder.as_markup() 