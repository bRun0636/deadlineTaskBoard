FROM node:18-alpine

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем package.json и package-lock.json
COPY package*.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код
COPY . .

# Открываем порт
EXPOSE 3000

# Создаем production сборку
RUN npm run build

# Устанавливаем serve для раздачи статических файлов
RUN npm install -g serve

# Запускаем production сервер
CMD ["serve", "-s", "build", "-l", "3000"] 