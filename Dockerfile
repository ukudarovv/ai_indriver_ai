# Используем более легкий базовый образ
FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libavcodec-dev \
    libavformat-dev \
    libswscale-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt для кэширования слоев
COPY requirements.txt .

# Устанавливаем зависимости с оптимизацией
RUN pip install --no-cache-dir --prefer-binary -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем директории для медиа файлов
RUN mkdir -p media processed_images static

# Настраиваем переменные окружения
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=car_analysis_project.settings

# Открываем порт
EXPOSE 8000

# Команда запуска (слушаем на всех интерфейсах)
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
