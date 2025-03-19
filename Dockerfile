FROM python:3.10-slim

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt для установки зависимостей
COPY requirements.txt .

# Устанавливаем зависимости Python
RUN pip install -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Указываем команду для запуска приложения
CMD ["python", "run.py"]