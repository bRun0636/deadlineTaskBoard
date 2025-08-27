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
        # Сначала пробуем создать таблицы через SQLAlchemy
        print("🔄 Создание таблиц через SQLAlchemy...")
        Base.metadata.create_all(bind=engine)
        
        # Проверяем, создались ли таблицы
        with engine.connect() as conn:
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            table_names = [table[0] for table in tables]
            
        if len(table_names) >= 9:  # Ожидаем минимум 9 таблиц
            print("✅ База данных успешно инициализирована через SQLAlchemy")
            print(f"Создано таблиц: {len(table_names)}")
            return
        else:
            print(f"⚠️ Создано только {len(table_names)} таблиц, ожидалось больше")
            print("🔄 Пробуем инициализацию через SQL файл...")
            
            # Если SQLAlchemy не создал все таблицы, используем SQL файл
            init_db_with_sql()
            
    except Exception as e:
        print(f"❌ Ошибка при инициализации через SQLAlchemy: {e}")
        print("🔄 Пробуем инициализацию через SQL файл...")
        init_db_with_sql()


def init_db_with_sql():
    """Инициализация базы данных с использованием SQL файла"""
    try:
        # Читаем SQL файл
        sql_file_path = os.path.join(os.path.dirname(__file__), '..', 'init_db.sql')
        
        if not os.path.exists(sql_file_path):
            print(f"❌ SQL файл не найден: {sql_file_path}")
            return
            
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        print("📄 SQL файл прочитан успешно")
        
        # Выполняем SQL команды
        with engine.connect() as conn:
            try:
                conn.execute(text(sql_content))
                conn.commit()
                print("✅ SQL файл выполнен успешно")
            except Exception as e:
                print(f"⚠️ Ошибка при выполнении SQL: {e}")
                # Попробуем выполнить по частям
                print("🔄 Пробуем выполнить по частям...")
                
                # Разделяем на блоки DO $$ ... END $$
                import re
                do_blocks = re.findall(r'DO \$\$.*?END \$\$;', sql_content, re.DOTALL)
                
                # Удаляем DO блоки из основного SQL
                sql_without_do = re.sub(r'DO \$\$.*?END \$\$;', '', sql_content, flags=re.DOTALL)
                
                # Выполняем DO блоки
                for i, block in enumerate(do_blocks):
                    try:
                        conn.execute(text(block))
                        print(f"✅ DO блок {i+1} выполнен успешно")
                    except Exception as e:
                        print(f"⚠️ DO блок {i+1} пропущен: {e}")
                
                # Выполняем остальной SQL
                if sql_without_do.strip():
                    try:
                        conn.execute(text(sql_without_do))
                        print("✅ Остальной SQL выполнен успешно")
                    except Exception as e:
                        print(f"⚠️ Ошибка в остальном SQL: {e}")
                
                conn.commit()
        
        # Проверяем результат
        with engine.connect() as conn:
            result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"))
            tables = result.fetchall()
            table_names = [table[0] for table in tables]
            
        print(f"✅ База данных успешно инициализирована. Создано таблиц: {len(table_names)}")
        print(f"Таблицы: {table_names}")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")


if __name__ == "__main__":
    init_db()
