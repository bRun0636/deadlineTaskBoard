from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура профиля
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data="edit_profile"),
            InlineKeyboardButton(text="📊 Статистика", callback_data="statistics")
        ],
        [
            InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 


def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура редактирования профиля
    """
    keyboard = [
        [
            InlineKeyboardButton(text="👤 Имя", callback_data="edit_first_name"),
            InlineKeyboardButton(text="📝 Фамилия", callback_data="edit_last_name")
        ],
        [
            InlineKeyboardButton(text="📧 Email", callback_data="edit_email"),
            InlineKeyboardButton(text="📱 Телефон", callback_data="edit_phone")
        ],
        [
            InlineKeyboardButton(text="🌍 Страна", callback_data="edit_country"),
            InlineKeyboardButton(text="💼 Тип", callback_data="edit_juridical_type")
        ],
        [
            InlineKeyboardButton(text="📊 Уровень", callback_data="edit_prof_level"),
            InlineKeyboardButton(text="💡 Навыки", callback_data="edit_skills")
        ],
        [
            InlineKeyboardButton(text="📄 Био", callback_data="edit_bio"),
            InlineKeyboardButton(text="📎 Резюме", callback_data="edit_resume")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад к профилю", callback_data="profile")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_juridical_type_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора типа юр. лица
    """
    keyboard = [
        [
            InlineKeyboardButton(text="👤 Физическое лицо", callback_data="juridical_individual"),
            InlineKeyboardButton(text="🏢 Юридическое лицо", callback_data="juridical_company")
        ],
        [
            InlineKeyboardButton(text="💼 ИП", callback_data="juridical_entrepreneur"),
            InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_prof_level_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора уровня профессионализма
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🟢 Начинающий", callback_data="prof_level_junior"),
            InlineKeyboardButton(text="🟡 Средний", callback_data="prof_level_middle")
        ],
        [
            InlineKeyboardButton(text="🟠 Высокий", callback_data="prof_level_senior"),
            InlineKeyboardButton(text="🔴 Эксперт", callback_data="prof_level_expert")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_country_keyboard() -> InlineKeyboardMarkup:
    """
    Клавиатура выбора страны
    """
    keyboard = [
        [
            InlineKeyboardButton(text="🇷🇺 Россия", callback_data="country_russia"),
            InlineKeyboardButton(text="🇰🇿 Казахстан", callback_data="country_kazakhstan")
        ],
        [
            InlineKeyboardButton(text="🇧🇾 Беларусь", callback_data="country_belarus"),
            InlineKeyboardButton(text="🇺🇦 Украина", callback_data="country_ukraine")
        ],
        [
            InlineKeyboardButton(text="🇦🇲 Армения", callback_data="country_armenia"),
            InlineKeyboardButton(text="🇦🇿 Азербайджан", callback_data="country_azerbaijan")
        ],
        [
            InlineKeyboardButton(text="🇬🇪 Грузия", callback_data="country_georgia"),
            InlineKeyboardButton(text="🇲🇩 Молдова", callback_data="country_moldova")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """
    Клавиатура подтверждения действия
    """
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_{action}"),
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{action}")
        ],
        [
            InlineKeyboardButton(text="🔙 Назад", callback_data="edit_profile")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 