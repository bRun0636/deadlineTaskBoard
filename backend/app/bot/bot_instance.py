import os
from aiogram import Bot

# Токен бота
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

# Создаем экземпляр бота
bot = Bot(token=BOT_TOKEN, parse_mode="HTML") 