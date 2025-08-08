#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import sys
import os

# Добавляем путь к приложению в sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import text
from app.database import engine, SessionLocal
from app.models.base import Base
from app.models.user import User
from app.models.board import Board
from app.models.column import Column
from app.models.task import Task
from app.models.order import Order
from app.models.proposal import Proposal
from app.models.message import Message
from app.models.task_status import TaskStatus
from app.models.task_type import TaskType


def init_db():
    """Инициализация базы данных"""
    try:
        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("✅ База данных успешно инициализирована")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        # Не выходим с ошибкой, так как таблицы могут уже существовать
        pass


if __name__ == "__main__":
    init_db()
