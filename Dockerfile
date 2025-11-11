FROM python:3.12-slim
WORKDIR /app

# 1. Установка системных зависимостей (компиляторы и dev-пакеты)
RUN apt update \
    && apt install -y build-essential python3-dev libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. Копируем файл с зависимостями
COPY requirements.txt .

# 3. Установка Python-зависимостей
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем остальной код
COPY . .

# 5. Команда запуска
CMD ["python", "bot.py"]