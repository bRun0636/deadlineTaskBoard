#!/usr/bin/env python3
"""
Скрипт для исправления паролей пользователей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.user import User
from app.models.user import User
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def fix_user_passwords():
    """Исправляет пароли пользователей"""
    db = SessionLocal()
    
    try:
        # Список пользователей и их паролей
        users_data = [
            {"username": "testuser", "password": "testpass123"},
            {"username": "customer", "password": "customer123"},
            {"username": "admin", "password": "testpass123"}
        ]
        
        for user_data in users_data:
            user = db.query(User).filter(User.username == user_data["username"]).first()
            if user:
                # Генерируем правильный хеш
                hashed_password = get_password_hash(user_data["password"])
                user.hashed_password = hashed_password
                print(f"✅ Обновлен пароль для пользователя: {user.username}")
            else:
                print(f"❌ Пользователь не найден: {user_data['username']}")
        
        db.commit()
        print("✅ Все пароли успешно обновлены!")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении паролей: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_user_passwords() 