# Инструкция по установке и запуску

## 🚀 Быстрый старт

### 1. Клонирование репозитория
```bash
git clone https://github.com/ukudarovv/ai_indriver_ai.git
cd ai_indriver_ai
```

### 2. Создание виртуального окружения
```bash
# Windows
python -m venv env
env\Scripts\activate

# Linux/Mac
python -m venv env
source env/bin/activate
```

### 3. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 4. Настройка API ключа Gemini
Создайте файл `.env` в корне проекта:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 5. Загрузка весов YOLO модели
Скачайте файл `best.pt` и поместите его в папку `CarDentDetector/Weights/`:
```bash
# Создайте папку если её нет
mkdir -p CarDentDetector/Weights

# Поместите файл best.pt в эту папку
# Файл должен быть около 83MB
```

### 6. Настройка Django
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser  # опционально для админки
```

### 7. Запуск сервера
```bash
python manage.py runserver
```

Откройте браузер и перейдите по адресу: http://127.0.0.1:8000/

## 📱 API Endpoints

### 1. Детальный анализ (Gemini + YOLO)
```
POST /api/analyze/
Content-Type: multipart/form-data
Body: image file
```

### 2. Анализ только Gemini (детальный)
```
POST /api/gemini-analyze/
Content-Type: multipart/form-data
Body: image file
```

### 3. Простой статус для мобильных приложений
```
POST /api/simple-status/
Content-Type: multipart/form-data
Body: image file
```

## 🔧 Структура проекта

```
ai_indriver_ai/
├── car_analysis_project/          # Django проект
├── car_detector/                  # Основное приложение
│   ├── models_ai/                 # AI модели
│   │   ├── gemini_analyzer.py     # Gemini анализатор
│   │   └── yolo_detector.py       # YOLO детектор
│   ├── templates/                 # HTML шаблоны
│   ├── services.py                # Бизнес-логика
│   └── views.py                   # API endpoints
├── CarDentDetector/               # YOLO модель
│   └── Weights/
│       └── best.pt                # Веса модели (83MB)
├── requirements.txt               # Зависимости
├── API_DOCUMENTATION.md          # Документация API
└── README.md                     # Описание проекта
```

## 🛠️ Требования

- Python 3.8+
- Django 5.0+
- Google Gemini API ключ
- YOLO веса модели (best.pt)

## 📋 Зависимости

Основные библиотеки:
- `django>=5.0.0`
- `google-generativeai>=0.8.0`
- `ultralytics>=8.0.0`
- `opencv-python>=4.8.0`
- `pillow>=10.0.0`
- `numpy>=1.24.0`

## 🚨 Важные замечания

1. **API ключ Gemini**: Обязательно настройте переменную окружения `GEMINI_API_KEY`
2. **YOLO веса**: Файл `best.pt` не включен в репозиторий из-за размера (83MB)
3. **Виртуальное окружение**: Не коммитьте папку `env/` в git
4. **Медиа файлы**: Папка `media/` создается автоматически при загрузке изображений

## 🔍 Тестирование

### Тест API через cURL
```bash
curl -X POST \
  http://127.0.0.1:8000/api/simple-status/ \
  -F "image=@path/to/your/car_image.jpg"
```

### Тест через Python
```python
import requests

url = "http://127.0.0.1:8000/api/simple-status/"
files = {'image': open('car_image.jpg', 'rb')}
response = requests.post(url, files=files)
print(response.json())
```

## 🐛 Решение проблем

### Ошибка "API key not found"
- Проверьте, что файл `.env` создан и содержит `GEMINI_API_KEY=your_key`
- Убедитесь, что переменная окружения загружается

### Ошибка "YOLO model not found"
- Проверьте, что файл `CarDentDetector/Weights/best.pt` существует
- Убедитесь, что файл не поврежден (размер ~83MB)

### Ошибка "Large files detected"
- Убедитесь, что папка `env/` исключена из git (добавлена в .gitignore)
- Не коммитьте большие файлы (>100MB)

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи Django сервера
2. Убедитесь, что все зависимости установлены
3. Проверьте настройки API ключей
4. Создайте issue в GitHub репозитории
