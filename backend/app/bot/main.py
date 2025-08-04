import logging
import asyncio
import os
from aiogram import Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer

from .bot_instance import bot
from .routers import register_routers
from .middlewares import register_middlewares
from .services.scheduler_service import SchedulerService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """
    Главная функция запуска бота
    """
    logger.info("Запуск бота...")
    
    # Создаем диспетчер
    dp = Dispatcher()
    
    # Регистрируем роутеры
    register_routers(dp)
    
    # Регистрируем middleware
    register_middlewares(dp)
    
    # Инициализируем планировщик задач
    scheduler_service = SchedulerService()
    await scheduler_service.start()
    
    # Запускаем бота
    logger.info("Бот запущен и готов к работе!")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main()) 