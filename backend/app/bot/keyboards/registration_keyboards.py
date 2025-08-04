from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_phone_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для получения номера телефона"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard

def get_role_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора роли"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👨‍💼 Заказчик", callback_data="role_customer")
    builder.button(text="👨‍💻 Исполнитель", callback_data="role_executor")
    builder.adjust(1)
    return builder.as_markup()

def get_country_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора страны"""
    builder = InlineKeyboardBuilder()
    countries = [
        ("🇷🇺 Россия", "russia"),
        ("🇺🇸 США", "usa"),
        ("🇪🇺 Европа", "europe"),
        ("🇰🇿 Казахстан", "kazakhstan"),
        ("🇧🇾 Беларусь", "belarus"),
        ("🇺🇦 Украина", "ukraine"),
        ("🌍 Другая", "other")
    ]
    
    for name, code in countries:
        builder.button(text=name, callback_data=f"country_{code}")
    
    builder.adjust(2)
    return builder.as_markup()

def get_juridical_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора юридического статуса"""
    builder = InlineKeyboardBuilder()
    builder.button(text="👤 Физическое лицо", callback_data="juridical_individual")
    builder.button(text="🏢 ООО", callback_data="juridical_llc")
    builder.button(text="💼 ИП", callback_data="juridical_ip")
    builder.adjust(1)
    return builder.as_markup()

def get_payment_types_keyboard(selected_types: list = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора типов оплаты"""
    if selected_types is None:
        selected_types = []
    
    builder = InlineKeyboardBuilder()
    payment_types = [
        ("💳 Банковская карта", "card"),
        ("💵 Наличные", "cash"),
        ("🏦 Банковский перевод", "bank_transfer"),
        ("₿ Криптовалюта", "crypto")
    ]
    
    for name, code in payment_types:
        if code in selected_types:
            builder.button(text=f"✅ {name}", callback_data=f"payment_toggle_{code}")
        else:
            builder.button(text=f"❌ {name}", callback_data=f"payment_toggle_{code}")
    
    builder.button(text="✅ Готово", callback_data="payment_done")
    builder.adjust(1)
    return builder.as_markup()

def get_prof_level_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора уровня профессионализма"""
    builder = InlineKeyboardBuilder()
    levels = [
        ("🟢 Junior", "junior"),
        ("🟡 Middle", "middle"),
        ("🟠 Senior", "senior"),
        ("🔴 Expert", "expert")
    ]
    
    for name, code in levels:
        builder.button(text=name, callback_data=f"prof_level_{code}")
    
    builder.adjust(2)
    return builder.as_markup()

def get_notification_types_keyboard(selected_types: list = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора типов уведомлений"""
    if selected_types is None:
        selected_types = []
    
    builder = InlineKeyboardBuilder()
    notification_types = [
        ("📋 Новые задачи", "new_tasks"),
        ("🔄 Обновления задач", "task_updates"),
        ("💬 Сообщения", "messages"),
        ("💰 Платежи", "payments"),
        ("🔔 Системные", "system")
    ]
    
    for name, code in notification_types:
        if code in selected_types:
            builder.button(text=f"✅ {name}", callback_data=f"notification_toggle_{code}")
        else:
            builder.button(text=f"❌ {name}", callback_data=f"notification_toggle_{code}")
    
    builder.button(text="✅ Завершить регистрацию", callback_data="registration_complete")
    builder.adjust(1)
    return builder.as_markup() 