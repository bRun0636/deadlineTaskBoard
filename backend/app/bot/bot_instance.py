import os
from aiogram import Bot
from aiogram.types import BotCommand

# Токен бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

# Список команд бота для отображения подсказок (без эмодзи для лучшей совместимости)
BOT_COMMANDS = [
    BotCommand(command="start", description="Главное меню"),
    BotCommand(command="menu", description="Меню команд"),
    BotCommand(command="help", description="Справка"),
    BotCommand(command="update_commands", description="Обновить команды"),
    BotCommand(command="me", description="Добавить резюме"),
    BotCommand(command="rating", description="Мой рейтинг"),
    BotCommand(command="contracts", description="Мои задачи в работе"),
    BotCommand(command="sub", description="Создать подписку"),
    BotCommand(command="push", description="Настроить подписки"),
    BotCommand(command="myusers", description="Мои исполнители"),
    BotCommand(command="newtask", description="Создать простую задачу"),
    BotCommand(command="newhardtask", description="Создать сложную задачу"),
    BotCommand(command="send", description="Отправить сообщение"),
    BotCommand(command="settings", description="Настройки"),
    BotCommand(command="stat", description="Статистика"),
    BotCommand(command="token", description="Управление токенами"),
    BotCommand(command="profile", description="Мой профиль"),
    BotCommand(command="tasks", description="Мои задачи"),
    BotCommand(command="orders", description="Заказы"),
    BotCommand(command="chat", description="Чаты"),
    BotCommand(command="admin", description="Админ-панель"),
]

async def set_bot_commands():
    """Установка команд бота для отображения подсказок"""
    try:
        await bot.set_my_commands(BOT_COMMANDS)
        return True
    except Exception as e:
        logger.error(f"Ошибка при установке команд: {e}")
        return False 