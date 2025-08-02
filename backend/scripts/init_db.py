"""
Скрипт для инициализации базы данных с начальными данными
"""

import sys
import os
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Base, User, Board, Task, TaskType, Column, UserRole
from app.crud.user import user_crud
from app.schemas.user import UserCreate

def init_db():
    """Инициализация базы данных"""
    # Применяем миграции Alembic
    try:
        print("Применяем миграции Alembic...")
        subprocess.run(["alembic", "upgrade", "head"], check=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        print("Миграции успешно применены!")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при применении миграций: {e}")
        # Если миграции не применились, создаем таблицы вручную
        print("Создаем таблицы вручную...")
        Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Создаем типы задач
        task_types = [
            {"name": "public", "display_name": "Публичная"},
            {"name": "private", "display_name": "Приватная"},
        ]
        for type_data in task_types:
            existing_type = db.query(TaskType).filter(TaskType.name == type_data["name"]).first()
            if not existing_type:
                db.add(TaskType(**type_data))
        db.commit()

        # Создаем колонки (статусы)
        columns = [
            {"name": "К выполнению", "order": 1},
            {"name": "В работе", "order": 2},
            {"name": "Проверка", "order": 3},
            {"name": "Баг", "order": 4},
            {"name": "Завершено", "order": 5},
        ]

        # Предварительно определим доску, для которой создаем колонки
        test_board = db.query(Board).filter(Board.title == "Тестовая доска").first()
        if not test_board:
            # Создаем доску, если её еще нет
            test_user = user_crud.get_by_username(db, username="testuser")
            if not test_user:
                user_data = UserCreate(
                    username="testuser",
                    email="test@example.com",
                    password="testpass123",
                    full_name="Тестовый Пользователь"
                )
                test_user = user_crud.create(db, user_data)
            test_board = Board(
                title="Тестовая доска",
                description="Доска для тестирования функциональности",
                owner_id=test_user.id,
                is_public=True
            )
            db.add(test_board)
            db.commit()
            db.refresh(test_board)

        # Создаем колонки
        for col_data in columns:
            existing_col = db.query(Column).filter(Column.name == col_data["name"], Column.board_id == test_board.id).first()
            if not existing_col:
                col = Column(**col_data, board_id=test_board.id)
                db.add(col)
        db.commit()

        # Создаем тестового пользователя
        test_user = user_crud.get_by_username(db, username="testuser")
        if not test_user:
            user_data = UserCreate(
                username="testuser",
                email="test@example.com",
                password="testpass123",
                full_name="Тестовый Пользователь",
                role=UserRole.EXECUTOR
            )
            test_user = user_crud.create(db, user_data)

        # Создаем тестовые задачи, указывая колонку по имени
        test_tasks = [
            {
                "title": "Настроить аутентификацию",
                "description": "Реализовать JWT аутентификацию для API",
                "column_name": "К выполнению",
                "priority": "medium",
                "budget": 1000.0,
                "tags": ["auth", "security"],
                "assigned_to_id": test_user.id,
            },
            {
                "title": "Создать API для задач",
                "description": "Разработать REST API для управления задачами",
                "column_name": "В работе",
                "priority": "high",
                "budget": 2000.0,
                "tags": ["api", "backend"],
                "assigned_to_id": test_user.id,
            },
            {
                "title": "Интегрировать с фронтендом",
                "description": "Подключить React приложение к API",
                "column_name": "Проверка",
                "priority": "high",
                "budget": 1500.0,
                "tags": ["frontend", "integration"],
                "assigned_to_id": test_user.id,
            },
            {
                "title": "Добавить drag-and-drop",
                "description": "Реализовать перетаскивание задач между колонками",
                "column_name": "Баг",
                "priority": "low",
                "budget": 800.0,
                "tags": ["ui", "ux"],
                "assigned_to_id": test_user.id,
            },
            {
                "title": "Деплой в продакшн",
                "description": "Развернуть приложение на сервере",
                "column_name": "Завершено",
                "priority": "low",
                "budget": 500.0,
                "tags": ["deployment", "devops"],
                "assigned_to_id": test_user.id,
            }
        ]

        for task_data in test_tasks:
            # Проверяем, есть ли уже такая задача
            existing_task = db.query(Task).filter(
                Task.title == task_data["title"],
                Task.board_id == test_board.id
            ).first()
            if not existing_task:
                # Находим колонку по имени
                column_obj = db.query(Column).filter(Column.name == task_data["column_name"], Column.board_id == test_board.id).first()
                if not column_obj:
                    print(f"Колонка '{task_data['column_name']}' не найдена, пропускаем задачу '{task_data['title']}'")
                    continue
                task = Task(
                    title=task_data["title"],
                    description=task_data["description"],
                    column_id=column_obj.id,
                    priority=task_data["priority"],
                    budget=task_data["budget"],
                    tags=task_data["tags"],
                    board_id=test_board.id,
                    created_by_id=test_user.id,
                    assigned_to_id=task_data["assigned_to_id"]
                )
                db.add(task)

        # Создаем тестового заказчика
        customer_user = user_crud.get_by_username(db, username="customer")
        if not customer_user:
            customer_data = UserCreate(
                username="customer",
                email="customer@example.com",
                password="customer123",
                full_name="Тестовый Заказчик",
                role=UserRole.CUSTOMER
            )
            customer_user = user_crud.create(db, customer_data)

        db.commit()
        print("База данных успешно инициализирована!")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()