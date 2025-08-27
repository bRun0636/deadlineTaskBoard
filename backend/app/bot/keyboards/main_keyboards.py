from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_main_menu_keyboard(user_role=None, is_admin: bool = False, is_linked: bool = True) -> InlineKeyboardMarkup:
    """Главное меню с учетом роли пользователя"""
    builder = InlineKeyboardBuilder()
    
    # Общие кнопки для всех пользователей
    builder.button(text="📋 Мои задачи", callback_data="my_tasks")
    builder.button(text="👤 Профиль", callback_data="profile")
    builder.button(text="⭐ Рейтинг", callback_data="rating")
    builder.button(text="💬 Сообщения", callback_data="messages")
    builder.button(text="⚙️ Настройки", callback_data="settings")
    
    # Получаем строковое значение роли
    role_value = user_role.value if hasattr(user_role, 'value') else str(user_role) if user_role else "executor"
    
    # Кнопки в зависимости от роли
    if role_value == "customer":
        # Для заказчиков - создание задач и заказов
        builder.button(text="📝 Создать задачу", callback_data="create_task_new")
        builder.button(text="📊 Заказы", callback_data="orders")
        builder.button(text="➕ Создать заказ", callback_data="create_order")
        builder.button(text="🤑 Мои исполнители", callback_data="my_executors")
    elif role_value == "executor":
        # Для исполнителей - просмотр заказов и подписки
        builder.button(text="📊 Доступные заказы", callback_data="available_orders")
        builder.button(text="💼 Мои предложения", callback_data="my_proposals")
        builder.button(text="📝 Создать задачу", callback_data="create_task_new")
    elif role_value == "admin":
        # Для администраторов - все функции
        builder.button(text="📝 Создать задачу", callback_data="create_task_new")
        builder.button(text="📊 Заказы", callback_data="orders")
        builder.button(text="➕ Создать заказ", callback_data="create_order")
        builder.button(text="🤑 Мои исполнители", callback_data="my_executors")

    # Добавляем кнопку привязки аккаунта для непривязанных пользователей
    if not is_linked:
        builder.button(text="🔗 Привязать аккаунт", callback_data="link_account")

    # Добавляем кнопку админ-панели только для администраторов
    if is_admin:
        builder.button(text="🔧 Админ-панель", callback_data="admin")

    builder.adjust(2)
    return builder.as_markup()

def get_tasks_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню задач"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📋 Мои задачи", callback_data="my_tasks")
    builder.button(text="➕ Создать задачу", callback_data="create_task")
    builder.button(text="📊 Все задачи", callback_data="all_tasks")
    builder.button(text="📈 Статистика задач", callback_data="task_statistics")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_orders_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню заказов"""
    builder = InlineKeyboardBuilder()
    builder.button(text="📦 Мои заказы", callback_data="my_orders")
    builder.button(text="🔍 Доступные заказы", callback_data="available_orders")
    builder.button(text="➕ Создать заказ", callback_data="create_order")
    builder.button(text="💼 Мои предложения", callback_data="my_proposals")
    builder.button(text="📈 Статистика заказов", callback_data="order_statistics")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_messages_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню сообщений"""
    builder = InlineKeyboardBuilder()
    builder.button(text="💬 Мои чаты", callback_data="my_chats")
    builder.button(text="📨 Новые сообщения", callback_data="new_messages")
    builder.button(text="📤 Отправить сообщение", callback_data="send_message")
    builder.button(text="📋 История сообщений", callback_data="message_history")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_rating_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню рейтинга"""
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ Мой рейтинг", callback_data="my_rating")
    builder.button(text="🏆 Топ исполнителей", callback_data="top_executors")
    builder.button(text="📊 Рейтинг заказчиков", callback_data="top_customers")
    builder.button(text="📈 Моя статистика", callback_data="my_statistics")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()

def get_settings_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню настроек"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🔔 Уведомления", callback_data="notification_settings")
    builder.button(text="🌍 Язык", callback_data="language_settings")
    builder.button(text="🔒 Приватность", callback_data="privacy_settings")
    builder.button(text="💰 Платежные методы", callback_data="payment_settings")
    builder.button(text="📱 Telegram настройки", callback_data="telegram_settings")
    builder.button(text="🔙 Главное меню", callback_data="main_menu")
    builder.adjust(1)
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

def get_commands_menu_keyboard() -> InlineKeyboardMarkup:
    """Меню команд в стиле изображения"""
    builder = InlineKeyboardBuilder()
    
    # Команды с эмодзи и описанием
    builder.button(
        text="💪 /me - добавить свое резюме из hh.ru или др.",
        callback_data="command_me"
    )
    builder.button(
        text="🙈 /rating - ваш текущий рейтинг",
        callback_data="command_rating"
    )
    builder.button(
        text="💪 /contracts - мои задачи в работе",
        callback_data="command_contracts"
    )
    builder.button(
        text="💪 /sub - создать подписку на задачи",
        callback_data="command_sub"
    )
    builder.button(
        text="💪 /push - перенастроить подписки на новые заказы",
        callback_data="command_push"
    )
    builder.button(
        text="🤑 /myusers - список моих исполнителей",
        callback_data="command_myusers"
    )
    builder.button(
        text="📝 /newtask - создать простую задачу",
        callback_data="command_newtask"
    )
    builder.button(
        text="🔧 /newhardtask - создать сложную задачу",
        callback_data="command_newhardtask"
    )
    builder.button(
        text="📤 /send - отправить сообщение",
        callback_data="command_send"
    )
    builder.button(
        text="⚙️ /settings - настройки",
        callback_data="command_settings"
    )
    builder.button(
        text="📊 /stat - статистика",
        callback_data="command_stat"
    )
    builder.button(
        text="🔑 /token - управление токенами",
        callback_data="command_token"
    )
    
    # Кнопка "Меню" внизу
    builder.button(
        text="🔙 Главное меню",
        callback_data="main_menu"
    )
    
    builder.adjust(1)  # По одной кнопке в строке
    return builder.as_markup() 