# 🚀 Деплой на Railway

## 📋 Быстрый старт

### 1. **Подготовка**
- Убедитесь, что проект загружен в Git
- Получите токен Telegram бота от @BotFather

### 2. **Регистрация на Railway**
1. Зайдите на [railway.app](https://railway.app)
2. Нажмите "Start a New Project"
3. Подключите GitHub аккаунт

### 3. **Добавление проекта**
1. Выберите репозиторий: `bRun0636/deadlineTaskBoard`
2. Railway автоматически определит Docker

### 4. **Настройка переменных окружения**
В Railway добавьте:
```env
POSTGRES_PASSWORD=ваш_сложный_пароль_здесь
SECRET_KEY=сгенерированный_ключ_здесь
TELEGRAM_BOT_TOKEN=ваш_токен_бота
ALLOWED_ORIGINS=["https://ваш-домен.railway.app"]
REACT_APP_API_URL=https://ваш-домен.railway.app/api/v1
```

### 5. **Генерация SECRET_KEY**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 6. **Запуск**
1. Railway автоматически запустит сборку
2. Дождитесь завершения (2-3 минуты)
3. Получите URL вашего приложения

## 🔧 Структура проекта

```
deadline-task-board/
├── backend/           # FastAPI backend
├── web-app/          # React frontend
├── railway-compose.yml  # Конфигурация для Railway
├── railway.json      # Настройки Railway
├── Dockerfile        # Многоэтапная сборка
├── docker-compose.yml # Локальная разработка
└── README.md
```

## 🌐 Доступ к приложению

После деплоя:
- **Веб-приложение:** `https://ваш-домен.railway.app`
- **API документация:** `https://ваш-домен.railway.app/docs`
- **Telegram бот:** отправьте `/start` вашему боту

## 🔍 Мониторинг

- **Логи:** В Railway Dashboard
- **Статус:** Автоматические проверки здоровья
- **Обновления:** Автоматически из Git

## 🚨 Возможные проблемы

### Проект не запускается
1. Проверьте переменные окружения
2. Убедитесь в корректности Telegram токена
3. Проверьте логи в Railway

### База данных не подключается
1. Проверьте `POSTGRES_PASSWORD`
2. Убедитесь, что сервис `db` запущен

### Telegram бот не отвечает
1. Проверьте `TELEGRAM_BOT_TOKEN`
2. Убедитесь, что бот не заблокирован

## 📞 Поддержка

При проблемах:
1. Проверьте логи в Railway Dashboard
2. Убедитесь в корректности переменных окружения
3. Проверьте статус всех сервисов
4. Обратитесь в поддержку Railway

---

**Готово!** Ваш проект будет доступен по адресу, предоставленному Railway. 