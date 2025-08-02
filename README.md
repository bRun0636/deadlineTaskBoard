# Deadline Task Board

Полнофункциональное веб-приложение для управления задачами с дедлайнами, построенное на React + FastAPI.

## 🚀 Возможности

- **Аутентификация** - регистрация, вход, управление профилем
- **Доски** - создание, редактирование, удаление досок
- **Задачи** - полный CRUD для задач с канбан-доской
- **Публичные доски** - просмотр публичных досок
- **Профили пользователей** - просмотр профилей
- **Современный UI** - адаптивный дизайн с темной темой

## 🛠 Технологии

### Frontend
- React 18
- React Router DOM
- React Query
- React Hook Form
- React DnD
- Tailwind CSS
- Lucide React
- Axios

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- JWT Authentication
- Alembic (миграции)

## 📦 Установка и запуск

### Вариант 1: Docker Compose (Рекомендуется)

1. **Клонируйте репозиторий**
```bash
git clone <repository-url>
cd deadline-task-board
```

2. **Запустите все сервисы**
```bash
docker-compose up -d
```

3. **Откройте приложение**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Документация**: http://localhost/docs
- **Nginx (прокси)**: http://localhost

### Вариант 2: Локальная разработка

1. **Установите зависимости**
```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../web-app
npm install
```

2. **Настройте базу данных**
```bash
# Создайте PostgreSQL базу
createdb deadline_task_board

# Инициализируйте данные
cd backend
python scripts/init_db.py
```

3. **Запустите сервисы**
```bash
# Backend (в одном терминале)
cd backend
uvicorn app.main:app --reload

# Frontend (в другом терминале)
cd web-app
npm start
```

### Вариант 3: Одна команда (с concurrently)

1. **Установите зависимости**
```bash
npm install
cd web-app && npm install
cd ../backend && pip install -r requirements.txt
```

2. **Запустите оба сервера**
```bash
npm run dev
```

## 🔐 Тестовые данные

После инициализации создается тестовый пользователь.
Данные для входа смотрите в файле `backend/scripts/init_db.py`

### 👑 Администратор

Для создания первого администратора выполните:
```bash
cd backend
python scripts/create_admin.py
```

⚠️ **ВАЖНО**: Измените пароли после первого входа!

## 📁 Структура проекта

```
deadline-task-board/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── auth/           # Authentication
│   │   ├── crud/           # Database operations
│   │   ├── models/         # Database models
│   │   └── schemas/        # Pydantic schemas
│   ├── scripts/            # Database scripts
│   └── requirements.txt    # Python dependencies
├── web-app/                # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── hooks/          # Custom hooks
│   │   └── services/       # API services
│   └── package.json        # Node dependencies
├── docker-compose.yml      # Docker configuration
└── nginx.conf             # Nginx configuration
```

## 🐳 Docker команды

```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Пересборка
docker-compose up -d --build

# Очистка данных
docker-compose down -v
```

## 🔧 Разработка

### Backend
```bash
cd backend

# Создание миграции
alembic revision --autogenerate -m "Description"

# Применение миграций
alembic upgrade head

# Запуск тестов
pytest
```

### Frontend
```bash
cd web-app

# Запуск в режиме разработки
npm start

# Сборка для продакшена
npm run build

# Запуск тестов
npm test
```

## 📚 API Endpoints

### Аутентификация
- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `GET /api/v1/auth/me` - Текущий пользователь

### Администратор (только для суперпользователей)
- `GET /api/v1/admin/stats` - Статистика системы
- `GET /api/v1/admin/users` - Все пользователи
- `GET /api/v1/admin/users/active` - Активные пользователи
- `PUT /api/v1/admin/users/{user_id}` - Обновление пользователя
- `DELETE /api/v1/admin/users/{user_id}` - Полное удаление пользователя
- `GET /api/v1/admin/boards` - Все доски
- `PUT /api/v1/admin/boards/{board_id}/activate` - Активировать доску
- `PUT /api/v1/admin/boards/{board_id}/deactivate` - Деактивировать доску
- `DELETE /api/v1/admin/boards/{board_id}` - Полное удаление доски

### Пользователи
- `GET /api/v1/users/` - Список пользователей
- `GET /api/v1/users/{id}` - Пользователь по ID
- `PUT /api/v1/users/{id}` - Обновление пользователя

### Доски
- `GET /api/v1/boards/` - Мои доски
- `GET /api/v1/boards/public` - Публичные доски
- `POST /api/v1/boards/` - Создание доски
- `GET /api/v1/boards/{id}` - Доска по ID
- `PUT /api/v1/boards/{id}` - Обновление доски
- `DELETE /api/v1/boards/{id}` - Удаление доски

### Задачи
- `GET /api/v1/tasks/` - Все задачи
- `GET /api/v1/tasks/my` - Мои задачи
- `GET /api/v1/tasks/assigned` - Назначенные мне
- `GET /api/v1/tasks/board/{id}` - Задачи доски
- `GET /api/v1/tasks/board/{id}/kanban` - Канбан доски
- `POST /api/v1/tasks/` - Создание задачи
- `PUT /api/v1/tasks/{id}` - Обновление задачи
- `PATCH /api/v1/tasks/{id}/status` - Изменение статуса
- `DELETE /api/v1/tasks/{id}` - Удаление задачи

## 🐛 Устранение неполадок

### Проблемы с Docker
```bash
# Очистка Docker
docker system prune -a

# Проверка портов
netstat -tulpn | grep :3000
netstat -tulpn | grep :8000
```

### Проблемы с базой данных
```bash
# Подключение к PostgreSQL
docker exec -it deadline_task_board_db psql -U dbuser -d deadline_task_board

# Проверка таблиц
\dt
```

### Проблемы с API
```bash
# Проверка логов
docker-compose logs api

# Проверка здоровья API
curl http://localhost:8000/
```

## 📄 Лицензия

MIT License

## 🤝 Поддержка

Если у вас возникли проблемы:
1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что все порты свободны
3. Проверьте, что PostgreSQL запущен
4. Убедитесь, что все переменные окружения настроены правильно 