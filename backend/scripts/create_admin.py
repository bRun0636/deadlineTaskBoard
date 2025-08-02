#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.models.user import User
from app.crud.user import user_crud

def create_admin():
    db = SessionLocal()
    try:
        # Проверяем, есть ли уже админы
        existing_admins = db.query(User).filter(User.is_superuser == True).count()
        if existing_admins > 0:
            print("Администраторы уже существуют в системе.")
            return

        # Создаем первого админа
        from app.schemas.user import UserCreate
        
        admin_data = UserCreate(
            username="admin",
            email="admin@example.com",
            password="admin123",
            full_name="Системный администратор"
        )

        # Проверяем, существует ли пользователь с таким username
        existing_user = user_crud.get_by_username(db, admin_data.username)
        if existing_user:
            print(f"Пользователь с username '{admin_data.username}' уже существует.")
            return

        # Создаем админа
        admin_user = user_crud.create(db, admin_data)
        
        # Устанавливаем права администратора
        admin_user.is_superuser = True
        admin_user.is_active = True
        db.commit()
        db.refresh(admin_user)
        print(f"Администратор создан успешно!")
        print(f"Username: {admin_user.username}")
        print(f"Email: {admin_user.email}")
        print(f"Password: {admin_data.password}")
        print("\n⚠️  ВАЖНО: Измените пароль после первого входа!")

    except Exception as e:
        print(f"Ошибка при создании администратора: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin() 