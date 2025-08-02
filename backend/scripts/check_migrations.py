#!/usr/bin/env python3
"""
Скрипт для проверки статуса миграций Alembic
"""

import sys
import os
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_migrations():
    """Проверяет статус миграций"""
    try:
        print("Проверяем статус миграций...")
        result = subprocess.run(
            ["alembic", "current"], 
            capture_output=True, 
            text=True, 
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode == 0:
            print("Текущая версия миграции:")
            print(result.stdout.strip())
        else:
            print("Ошибка при проверке миграций:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Ошибка: {e}")

def show_migration_history():
    """Показывает историю миграций"""
    try:
        print("\nИстория миграций:")
        result = subprocess.run(
            ["alembic", "history"], 
            capture_output=True, 
            text=True, 
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )
        
        if result.returncode == 0:
            print(result.stdout)
        else:
            print("Ошибка при получении истории миграций:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    check_migrations()
    show_migration_history() 