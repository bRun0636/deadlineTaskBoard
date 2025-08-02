#!/usr/bin/env python3
"""
Скрипт для обновления ролей существующих пользователей после добавления системы ролей.
Устанавливает роль 'executor' для всех существующих пользователей.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.user import User, UserRole

def update_user_roles():
    """Обновляет роли всех существующих пользователей"""
    db = SessionLocal()
    
    try:
        # Получаем всех пользователей без роли
        users_without_role = db.query(User).filter(User.role.is_(None)).all()
        
        if not users_without_role:
            print("Все пользователи уже имеют роль.")
            return
        
        print(f"Найдено {len(users_without_role)} пользователей без роли.")
        
        # Устанавливаем роль 'executor' для всех пользователей
        for user in users_without_role:
            user.role = UserRole.EXECUTOR
            print(f"Обновлен пользователь: {user.username} -> {user.role.value}")
        
        # Сохраняем изменения
        db.commit()
        print(f"Успешно обновлено {len(users_without_role)} пользователей.")
        
    except Exception as e:
        print(f"Ошибка при обновлении ролей: {e}")
        db.rollback()
    finally:
        db.close()

def set_admin_role(username):
    """Устанавливает роль администратора для указанного пользователя"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"Пользователь {username} не найден.")
            return
        
        user.role = UserRole.ADMIN
        db.commit()
        print(f"Пользователь {username} получил роль администратора.")
        
    except Exception as e:
        print(f"Ошибка при установке роли администратора: {e}")
        db.rollback()
    finally:
        db.close()

def set_customer_role(username):
    """Устанавливает роль заказчика для указанного пользователя"""
    db = SessionLocal()
    
    try:
        user = db.query(User).filter(User.username == username).first()
        
        if not user:
            print(f"Пользователь {username} не найден.")
            return
        
        user.role = UserRole.CUSTOMER
        db.commit()
        print(f"Пользователь {username} получил роль заказчика.")
        
    except Exception as e:
        print(f"Ошибка при установке роли заказчика: {e}")
        db.rollback()
    finally:
        db.close()

def show_user_roles():
    """Показывает роли всех пользователей"""
    db = SessionLocal()
    
    try:
        users = db.query(User).all()
        
        print("\nРоли пользователей:")
        print("-" * 50)
        for user in users:
            role = user.role.value if user.role else "Не установлена"
            print(f"{user.username}: {role}")
        
    except Exception as e:
        print(f"Ошибка при получении ролей: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "update":
            update_user_roles()
        elif command == "admin" and len(sys.argv) > 2:
            set_admin_role(sys.argv[2])
        elif command == "customer" and len(sys.argv) > 2:
            set_customer_role(sys.argv[2])
        elif command == "show":
            show_user_roles()
        else:
            print("Использование:")
            print("  python update_user_roles.py update     - Обновить роли всех пользователей")
            print("  python update_user_roles.py admin USER - Установить роль администратора")
            print("  python update_user_roles.py customer USER - Установить роль заказчика")
            print("  python update_user_roles.py show       - Показать роли всех пользователей")
    else:
        print("Использование:")
        print("  python update_user_roles.py update     - Обновить роли всех пользователей")
        print("  python update_user_roles.py admin USER - Установить роль администратора")
        print("  python update_user_roles.py customer USER - Установить роль заказчика")
        print("  python update_user_roles.py show       - Показать роли всех пользователей") 