# Docker Setup для AI Car Analysis

## 🐳 Быстрый старт с Docker

### 1. Создание .env файла
```bash
# Создайте файл .env в корне проекта
echo "GEMINI_API_KEY=your_gemini_api_key_here" > .env
```

### 2. Сборка и запуск (обычный Dockerfile)
```bash
# Сборка образа
docker build -t ai-car-analysis .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env ai-car-analysis
```

### 3. Сборка и запуск (оптимизированный)
```bash
# Сборка оптимизированного образа
docker build -f Dockerfile.optimized -t ai-car-analysis-optimized .

# Запуск контейнера
docker run -p 8000:8000 --env-file .env ai-car-analysis-optimized
```

### 4. Использование Docker Compose (рекомендуется)
```bash
# Запуск с docker-compose
docker-compose up --build

# Запуск в фоновом режиме
docker-compose up -d --build
```

## 🔧 Решение проблем с местом на диске

### Проблема: "No space left on device"

**Причины:**
- PyTorch и OpenCV занимают много места
- Docker не очищает промежуточные слои
- Большие зависимости в requirements.txt

**Решения:**

#### 1. Используйте оптимизированный Dockerfile
```bash
docker build -f Dockerfile.optimized -t ai-car-analysis .
```

#### 2. Очистите Docker кэш
```bash
# Удалите неиспользуемые образы
docker system prune -a

# Удалите все контейнеры и образы
docker system prune -a --volumes
```

#### 3. Увеличьте место на диске Docker
- **Windows/Mac**: В Docker Desktop → Settings → Resources → Advanced
- **Linux**: Увеличьте размер диска для Docker

#### 4. Используйте .dockerignore
Файл `.dockerignore` исключает ненужные файлы из контекста сборки.

## 📦 Оптимизация размера образа

### Минимальные зависимости
Используется `requirements-minimal.txt` вместо полного `requirements.txt`:

```txt
# Только необходимые зависимости
django>=5.0.0
google-generativeai>=0.8.0
numpy>=1.23.5
pillow>=10.3.0
opencv-python-headless>=4.8.0
ultralytics>=8.2.34
```

### Многоэтапная сборка
`Dockerfile.optimized` использует многоэтапную сборку:
- **Builder stage**: Сборка зависимостей
- **Final stage**: Только необходимые файлы

## 🚀 Команды для разработки

### Сборка без кэша
```bash
docker build --no-cache -t ai-car-analysis .
```

### Просмотр размера образа
```bash
docker images ai-car-analysis
```

### Запуск с монтированием папок
```bash
docker run -p 8000:8000 \
  -v $(pwd)/media:/app/media \
  -v $(pwd)/CarDentDetector/Weights:/app/CarDentDetector/Weights:ro \
  --env-file .env \
  ai-car-analysis
```

### Подключение к контейнеру
```bash
docker exec -it <container_id> bash
```

## 🔍 Мониторинг ресурсов

### Проверка использования места
```bash
# Размер Docker данных
docker system df

# Детальная информация
docker system df -v
```

### Очистка неиспользуемых ресурсов
```bash
# Безопасная очистка
docker system prune

# Агрессивная очистка (удаляет все)
docker system prune -a --volumes
```

## 📋 Требования к системе

### Минимальные требования:
- **RAM**: 4GB (рекомендуется 8GB)
- **Диск**: 10GB свободного места
- **Docker**: 20.10.0+

### Рекомендуемые настройки Docker:
- **Memory**: 4GB
- **CPU**: 2 cores
- **Disk**: 20GB

## 🛠️ Troubleshooting

### Ошибка "No space left on device"
1. Увеличьте место на диске Docker
2. Используйте `Dockerfile.optimized`
3. Очистите Docker кэш
4. Используйте `.dockerignore`

### Ошибка "API key not found"
1. Проверьте файл `.env`
2. Убедитесь, что переменная `GEMINI_API_KEY` установлена

### Ошибка "YOLO model not found"
1. Монтируйте папку с весами: `-v ./CarDentDetector/Weights:/app/CarDentDetector/Weights:ro`
2. Убедитесь, что файл `best.pt` существует

### Медленная работа
1. Увеличьте RAM для Docker
2. Используйте SSD диск
3. Закройте другие приложения

## 📊 Сравнение размеров образов

| Dockerfile | Размер | Время сборки | Рекомендация |
|------------|--------|--------------|--------------|
| Dockerfile | ~2.5GB | 5-10 мин | Для разработки |
| Dockerfile.optimized | ~1.8GB | 8-15 мин | Для продакшена |
| requirements-minimal.txt | ~1.2GB | 3-5 мин | Минимальная версия |
