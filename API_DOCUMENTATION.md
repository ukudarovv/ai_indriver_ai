# API Документация

## 1. Gemini API для анализа автомобилей (детальный)

### Endpoint
```
POST /api/gemini-analyze/
```

### Описание
API endpoint для анализа изображений автомобилей с помощью модели Gemini. Возвращает детальную информацию о состоянии автомобиля, включая повреждения, чистоту и условия съемки.

### Параметры запроса

#### Form Data
- `image` (file, обязательный) - Изображение автомобиля в формате JPG, JPEG, PNG или WebP

### Пример запроса

#### cURL
```bash
curl -X POST \
  http://127.0.0.1:8000/api/gemini-analyze/ \
  -F "image=@path/to/your/car_image.jpg"
```

#### Python (requests)
```python
import requests

url = "http://127.0.0.1:8000/api/gemini-analyze/"
files = {'image': open('car_image.jpg', 'rb')}

response = requests.post(url, files=files)
data = response.json()

print(f"Статус: {data['status']}")
print(f"Время обработки: {data['processing_time']}с")
```

#### JavaScript (fetch)
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);

fetch('http://127.0.0.1:8000/api/gemini-analyze/', {
    method: 'POST',
    body: formData
})
.then(response => response.json())
.then(data => {
    console.log('Результат:', data);
});
```

### Формат ответа

#### Успешный ответ (200 OK)
```json
{
    "status": "success",
    "model": "gemini",
    "processing_time": 4.57,
    "results": {
        "integrity": {
            "label": "damaged",
            "confidence": 0.999
        },
        "cleanliness": {
            "label": "slightly_dirty",
            "confidence": 0.95
        },
        "damage_details": {
            "overall_confidence": 0.95,
            "parts": [
                {
                    "part": "hood",
                    "type": "dent",
                    "confidence": 0.99,
                    "bbox": [0.2, 0.1, 0.6, 0.4],
                    "other_desc": null
                },
                {
                    "part": "bumper_front",
                    "type": "broken_part",
                    "confidence": 0.98,
                    "bbox": [0.1, 0.5, 0.9, 0.8],
                    "other_desc": null
                }
            ]
        },
        "environment": {
            "weather": "sunny",
            "lighting": "strong_glare",
            "glare_coverage_pct": 0.15,
            "wet_surface": false,
            "wetness_pct": 0.0,
            "raindrops_visible": false,
            "reflections_strong": true,
            "confidence": 0.9
        },
        "uncertain": false,
        "notes": ""
    }
}
```

#### Ошибка (400 Bad Request)
```json
{
    "error": "No image provided"
}
```

#### Ошибка (400 Bad Request)
```json
{
    "error": "File must be an image. Got extension: .txt"
}
```

#### Ошибка сервера (500 Internal Server Error)
```json
{
    "status": "error",
    "error": "Gemini analysis failed: API key not found"
}
```

### Описание полей ответа

#### integrity
- `label` - Общая оценка целостности: "damaged" или "undamaged"
- `confidence` - Уверенность в оценке (0.0 - 1.0)

#### cleanliness
- `label` - Оценка чистоты: "clean", "slightly_dirty" или "dirty"
- `confidence` - Уверенность в оценке (0.0 - 1.0)

#### damage_details
- `overall_confidence` - Общая уверенность в анализе повреждений
- `parts` - Массив найденных повреждений

#### parts (каждое повреждение)
- `part` - Часть автомобиля (например: "hood", "bumper_front", "headlight_left")
- `type` - Тип повреждения (например: "dent", "scratch", "broken_part")
- `confidence` - Уверенность в обнаружении (0.0 - 1.0)
- `bbox` - Координаты повреждения [x1, y1, x2, y2] в нормализованном формате (0.0 - 1.0)
- `other_desc` - Описание, если тип повреждения "other"

#### environment
- `weather` - Погодные условия: "sunny", "cloudy", "rain", "snow", "fog", "night", "indoor", "unknown"
- `lighting` - Освещение: "normal", "low_light", "strong_glare", "backlight", "mixed", "artificial"
- `glare_coverage_pct` - Процент покрытия бликами (0.0 - 1.0)
- `wet_surface` - Влажная поверхность (boolean)
- `wetness_pct` - Процент влажности (0.0 - 1.0)
- `raindrops_visible` - Видны ли капли дождя (boolean)
- `reflections_strong` - Сильные отражения (boolean)
- `confidence` - Уверенность в оценке условий (0.0 - 1.0)

### Коды ответов
- `200` - Успешный анализ
- `400` - Ошибка в запросе (нет изображения, неподдерживаемый формат)
- `500` - Внутренняя ошибка сервера

### Ограничения
- Максимальный размер файла: определяется настройками Django
- Поддерживаемые форматы: JPG, JPEG, PNG, WebP
- Время обработки: обычно 3-10 секунд в зависимости от сложности изображения

### Примеры использования

#### Проверка повреждений
```python
response = requests.post(url, files={'image': open('damaged_car.jpg', 'rb')})
data = response.json()

if data['status'] == 'success':
    results = data['results']
    
    # Проверяем целостность
    if results['integrity']['label'] == 'damaged':
        print("Автомобиль поврежден!")
        
    # Считаем повреждения
    damage_count = len(results['damage_details']['parts'])
    print(f"Найдено {damage_count} повреждений")
    
    # Выводим детали
    for part in results['damage_details']['parts']:
        print(f"- {part['part']}: {part['type']} ({part['confidence']*100:.1f}%)")
```

#### Анализ условий съемки
```python
environment = data['results']['environment']
print(f"Погода: {environment['weather']}")
print(f"Освещение: {environment['lighting']}")
print(f"Блики: {environment['glare_coverage_pct']*100:.1f}%")
```

---

## 2. Simple Status API для мобильных приложений

### Endpoint
```
POST /api/simple-status/
```

### Описание
Упрощенный API endpoint для мобильных приложений. Возвращает краткий и понятный статус автомобиля на русском языке.

### Параметры запроса

#### Form Data
- `image` (file, обязательный) - Изображение автомобиля в формате JPG, JPEG, PNG или WebP

### Пример запроса

#### cURL
```bash
curl -X POST \
  http://127.0.0.1:8000/api/simple-status/ \
  -F "image=@path/to/your/car_image.jpg"
```

#### Python (requests)
```python
import requests

url = "http://127.0.0.1:8000/api/simple-status/"
files = {'image': open('car_image.jpg', 'rb')}

response = requests.post(url, files=files)
data = response.json()

print(f"Статус: {data['car_status_text']}")
print(f"Повреждений: {data['damage_count']}")
print(f"Чистота: {data['cleanliness']}")
```

### Формат ответа

#### Успешный ответ (200 OK)
```json
{
    "status": "success",
    "model": "gemini",
    "processing_time": 4.2,
    "analysis_text": "🚗 АНАЛИЗ АВТОМОБИЛЯ\n\n📊 ОБЩЕЕ СОСТОЯНИЕ:\n• Целостность: Поврежден (99.9%)\n• Чистота: слегка грязный (95.0%)\n\n🔍 ДЕТАЛИ ПОВРЕЖДЕНИЙ:\n• Найдено повреждений: 4\n• Общая уверенность: 95.0%\n\n📋 СПИСОК ПОВРЕЖДЕНИЙ:\n1. Капот: Вмятина (99.0%)\n2. Передний бампер: Другое (crushed) (98.0%)\n3. Левая фара: Разбитое стекло (95.0%)\n4. Левое крыло: Вмятина (90.0%)\n\n🌤️ УСЛОВИЯ СЪЕМКИ:\n• Погода: Солнечно\n• Освещение: Сильные блики\n• Блики: 20.0%\n• Влажность: 0.0%\n• Уверенность: 90.0%\n\n⏱️ Время обработки: 4.2с",
    "summary": {
        "integrity": "Поврежден",
        "cleanliness": "слегка грязный",
        "damage_count": 4,
        "weather": "Солнечно",
        "lighting": "Сильные блики"
    }
}
```

#### Пример для хорошего состояния
```json
{
    "status": "success",
    "model": "gemini",
    "processing_time": 3.8,
    "analysis_text": "🚗 АНАЛИЗ АВТОМОБИЛЯ\n\n📊 ОБЩЕЕ СОСТОЯНИЕ:\n• Целостность: В хорошем состоянии (95.5%)\n• Чистота: чистый (88.0%)\n\n🔍 ДЕТАЛИ ПОВРЕЖДЕНИЙ:\n• Найдено повреждений: 0\n• Общая уверенность: 95.0%\n\n✅ Повреждений не обнаружено\n\n🌤️ УСЛОВИЯ СЪЕМКИ:\n• Погода: Солнечно\n• Освещение: Нормальное\n• Блики: 5.0%\n• Влажность: 0.0%\n• Уверенность: 85.0%\n\n⏱️ Время обработки: 3.8с",
    "summary": {
        "integrity": "В хорошем состоянии",
        "cleanliness": "чистый",
        "damage_count": 0,
        "weather": "Солнечно",
        "lighting": "Нормальное"
    }
}
```

### Описание полей ответа

- `status` - Статус запроса: "success" или "error"
- `model` - Используемая модель: "gemini"
- `processing_time` - Время обработки в секундах
- `analysis_text` - **Готовый текстовый отчет** с полным анализом автомобиля на русском языке
- `summary` - Краткая сводка основных параметров

#### summary (краткая сводка)
- `integrity` - Статус целостности: "Поврежден" или "В хорошем состоянии"
- `cleanliness` - Уровень чистоты: "чистый", "слегка грязный", "грязный"
- `damage_count` - Количество найденных повреждений
- `weather` - Погодные условия на русском языке
- `lighting` - Освещение на русском языке

### Формат analysis_text

Текстовый отчет включает:
- 🚗 **Общее состояние** - целостность и чистота с процентами уверенности
- 🔍 **Детали повреждений** - количество и общая уверенность
- 📋 **Список повреждений** - каждое повреждение с частью автомобиля, типом и уверенностью
- 🌤️ **Условия съемки** - погода, освещение, блики, влажность
- ⏱️ **Время обработки** - сколько секунд занял анализ
- 📝 **Заметки** - дополнительные комментарии (если есть)

### Примеры использования для мобильного приложения

#### React Native / Flutter
```javascript
const analyzeCar = async (imageUri) => {
    const formData = new FormData();
    formData.append('image', {
        uri: imageUri,
        type: 'image/jpeg',
        name: 'car_image.jpg'
    });

    try {
        const response = await fetch('http://127.0.0.1:8000/api/simple-status/', {
            method: 'POST',
            body: formData,
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        });

        const data = await response.json();
        
        if (data.status === 'success') {
            // Показываем готовый текстовый отчет
            showAnalysisText(data.analysis_text);
            
            // Или используем краткую сводку
            showSummary(data.summary);
        }
    } catch (error) {
        console.error('Ошибка анализа:', error);
    }
};
```

#### Android (Java)
```java
public void analyzeCar(Bitmap image) {
    // Создаем multipart запрос
    MultipartBody.Builder builder = new MultipartBody.Builder()
        .setType(MultipartBody.FORM);
    
    ByteArrayOutputStream baos = new ByteArrayOutputStream();
    image.compress(Bitmap.CompressFormat.JPEG, 100, baos);
    byte[] imageBytes = baos.toByteArray();
    
    RequestBody imageBody = RequestBody.create(
        MediaType.parse("image/jpeg"), 
        imageBytes
    );
    
    builder.addFormDataPart("image", "car_image.jpg", imageBody);
    
    Request request = new Request.Builder()
        .url("http://127.0.0.1:8000/api/simple-status/")
        .post(builder.build())
        .build();
    
    client.newCall(request).enqueue(new Callback() {
        @Override
        public void onResponse(Call call, Response response) throws IOException {
            String jsonData = response.body().string();
            JSONObject json = new JSONObject(jsonData);
            
            runOnUiThread(() -> {
                String statusText = json.getString("car_status_text");
                int damageCount = json.getInt("damage_count");
                String cleanliness = json.getString("cleanliness");
                
                // Обновляем UI
                statusTextView.setText(statusText);
                damageCountTextView.setText("Повреждений: " + damageCount);
                cleanlinessTextView.setText("Чистота: " + cleanliness);
            });
        }
        
        @Override
        public void onFailure(Call call, IOException e) {
            // Обработка ошибки
        }
    });
}
```

### Коды ответов
- `200` - Успешный анализ
- `400` - Ошибка в запросе (нет изображения, неподдерживаемый формат)
- `500` - Внутренняя ошибка сервера
