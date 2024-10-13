# Указываем базовый образ
FROM python:3.9-slim

# Устанавливаем зависимости системы
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    libssl-dev \
    libffi-dev \
    libgmp-dev

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с зависимостями
COPY pyproject.toml poetry.lock /app/

# Устанавливаем Poetry
RUN pip install poetry

# Устанавливаем зависимости проекта через Poetry
RUN poetry config virtualenvs.create false \
    && poetry install --only main --no-interaction --no-ansi

# Копируем весь проект в контейнер
COPY . /app

# Expose порта для приложения
EXPOSE 8000

# Запускаем приложение с uvicorn
CMD ["uvicorn", "teleport_webrtc.main:app", "--host", "0.0.0.0", "--port", "8000"]