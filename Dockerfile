# Многоэтапная сборка для оптимизации
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY web-app/package*.json ./
RUN npm ci --only=production
COPY web-app/ ./
RUN npm run build

FROM python:3.11-slim AS backend-builder
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./

# Финальный образ
FROM python:3.11-slim
WORKDIR /app

# Устанавливаем Node.js для запуска frontend
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копируем собранный frontend
COPY --from=frontend-builder /app/frontend/build ./frontend/build
COPY --from=frontend-builder /app/frontend/package*.json ./frontend/

# Копируем backend
COPY --from=backend-builder /app/backend ./backend
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Копируем docker-compose
COPY docker-compose.yml ./
COPY railway.json ./

# Устанавливаем зависимости для frontend
WORKDIR /app/frontend
RUN npm ci --only=production

# Возвращаемся в корень
WORKDIR /app

# Открываем порты
EXPOSE 3000 8000

# Команда запуска
CMD ["docker-compose", "up", "-d"] 