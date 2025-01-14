# Используем официальный slim Python
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

# Экспонируем порт для приложения FastAPI
EXPOSE 8080

# Устанавливаем переменную окружения для использования сертификата
ARG DATABASE_URL

ENV DATABASE_URL=$DATABASE_URL

# Запускаем сервер с помощью uvicorn
ENTRYPOINT ["sh", "/app/entrypoint.sh"]