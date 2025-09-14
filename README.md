# Car Analysis System

Система анализа автомобилей с использованием двух AI моделей: Google Gemini и YOLO.

## Возможности

- **Двойной анализ автомобилей** с помощью Google Gemini AI + YOLO
- **Детальный анализ** с помощью Google Gemini AI (целостность, чистота, условия съемки)
- **Обнаружение повреждений** с помощью обученной YOLO модели (17 типов повреждений)
- **Сравнение результатов** от обеих моделей
- **Веб-интерфейс** для загрузки изображений и просмотра результатов
- **Админ-панель** для управления анализами
- **API** для программного доступа

## Установка

1. **Клонируйте репозиторий:**
```bash
git clone <repository-url>
cd ai-driver
```

2. **Создайте виртуальное окружение:**
```bash
python -m venv env
```

3. **Активируйте виртуальное окружение:**
```bash
# Windows
env\Scripts\activate

# Linux/Mac
source env/bin/activate
```

4. **Установите зависимости:**
```bash
pip install -r requirements.txt
```

5. **Настройте API ключ Gemini:**
   - Откройте файл `gemini_car_state.py`
   - Замените `api_key = "YOUR_API_KEY"` на ваш реальный API ключ

6. **Примените миграции Django:**
```bash
python manage.py migrate
```

7. **Создайте суперпользователя (опционально):**
```bash
python manage.py createsuperuser
```

## Запуск

1. **Запустите Django сервер:**
```bash
python manage.py runserver
```

2. **Откройте браузер и перейдите по адресу:**
```
http://127.0.0.1:8000/
```

## Использование

### Веб-интерфейс

1. **Главная страница** - переход к двойному анализу
2. **Двойной анализ** - загрузите изображение и получите анализ от обеих моделей
3. **Страница результатов** - просмотрите детальный анализ с сравнением
4. **Список анализов** - история всех проведенных анализов

### API

**Endpoint:** `POST /api/analyze/`

**Параметры:**
- `image` - файл изображения (multipart/form-data)

**Ответ:**
```json
{
    "success": true,
    "results": {
        "gemini_results": {
            "integrity": {
                "label": "damaged",
                "confidence": 0.999
            },
            "cleanliness": {
                "label": "slightly_dirty", 
                "confidence": 0.95
            },
            "damage_details": {
                "parts": [...]
            },
            "environment": {...}
        },
        "yolo_results": {
            "detections": [...],
            "average_confidence": 0.85
        },
        "processing_time": 3.2
    }
}
```

## Структура проекта

```
ai-driver/
├── car_analysis_project/     # Django проект
├── car_detector/            # Django приложение
│   ├── models.py           # Модели данных
│   ├── views.py            # Представления
│   ├── services.py         # Сервисы анализа
│   └── templates/          # HTML шаблоны
├── CarDentDetector/        # YOLO модель
│   ├── CarDentDetector.py  # Основной класс
│   └── Weights/           # Веса модели
├── gemini_car_state.py     # Gemini интеграция
├── requirements.txt        # Зависимости
└── manage.py              # Django управление
```

## Модели анализа

### Gemini AI
- **Целостность:** damaged/undamaged
- **Чистота:** clean/slightly_dirty/dirty  
- **Детали повреждений:** части кузова и типы повреждений
- **Условия съемки:** погода, освещение, блики

### YOLO Detection
- **Обнаружение объектов:** координаты и уверенность
- **Классификация:** типы повреждений
- **Статистика:** количество и средняя уверенность

## Админ-панель

Доступна по адресу: `http://127.0.0.1:8000/admin/`

Возможности:
- Просмотр всех анализов
- Фильтрация по статусу и дате
- Поиск по заметкам
- Экспорт данных

## Технические детали

- **Django 5.2+** - веб-фреймворк
- **Google Generative AI** - анализ изображений
- **YOLO** - обнаружение объектов
- **Bootstrap 5** - UI компоненты
- **SQLite** - база данных (по умолчанию)

## Лицензия

MIT License
