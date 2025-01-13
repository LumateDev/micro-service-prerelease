# Используем официальный slim Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта в контейнер

COPY ./requirements.txt .


# Устанавливаем рабочие зависимости
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Экспонируем порт для приложения FastAPI
EXPOSE 8080

# Устанавливаем переменную окружения для использования сертификата
ARG DATABASE_URL

ENV DATABASE_URL = $DATABASE_URL

# Запускаем сервер с помощью uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]