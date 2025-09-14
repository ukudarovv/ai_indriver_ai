# car_detector/models_ai/gemini_analyzer.py
import os
import io
import re
from typing import Dict, Any
from PIL import Image

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("Warning: google-generativeai not available. Gemini analysis will be disabled.")


class GeminiAnalyzer:
    """Gemini анализатор для детального анализа автомобилей"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or "AIzaSyBcHZOH8nT045oOgdefL3iNOyJc0n0jgfQ"
        self.model_name = "gemini-1.5-flash"
        self.available = False
        
        if GEMINI_AVAILABLE and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.available = True
                print("Gemini analyzer initialized successfully")
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
    
    def load_as_jpeg_bytes(self, image_path: str, quality: int = 92) -> bytes:
        """Конвертирует изображение в JPEG байты"""
        with Image.open(image_path) as im:
            im = im.convert("RGB")
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=quality)
            return buf.getvalue()
    
    def analyze(self, image_path: str) -> Dict[str, Any]:
        """
        Анализирует изображение автомобиля
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Результаты анализа
        """
        if not self.available:
            return {
                'error': 'Gemini analyzer not available',
                'integrity': {'label': 'unknown', 'confidence': 0.0},
                'cleanliness': {'label': 'unknown', 'confidence': 0.0},
                'damage_details': {'parts': []},
                'environment': {},
                'uncertain': True,
                'notes': 'Gemini analyzer not available'
            }
        
        try:
            # Загружаем изображение
            image_bytes = self.load_as_jpeg_bytes(image_path)
            
            # Создаем модель
            model = genai.GenerativeModel(self.model_name)
            
            # Промпт для анализа
            prompt = self._get_analysis_prompt()
            
            # Выполняем анализ
            response = model.generate_content([
                {
                    "mime_type": "image/jpeg",
                    "data": image_bytes
                },
                prompt
            ])
            
            # Парсим результат
            return self._parse_response(response.text)
            
        except Exception as e:
            return {
                'error': f'Analysis failed: {str(e)}',
                'integrity': {'label': 'unknown', 'confidence': 0.0},
                'cleanliness': {'label': 'unknown', 'confidence': 0.0},
                'damage_details': {'parts': []},
                'environment': {},
                'uncertain': True,
                'notes': f'Analysis error: {str(e)}'
            }
    
    def _get_analysis_prompt(self) -> str:
        """Возвращает промпт для анализа"""
        return """Ты — строгий визуальный аудитор фото автомобиля. На вход ОДНО фото.
Верни ТОЛЬКО JSON согласно схеме ниже.

ЗАДАЧИ
1) integrity: damaged|undamaged — общая оценка целостности.
2) cleanliness: clean|slightly_dirty|dirty — оценка чистоты по доле видимой грязи.
3) damage_details: перечисли повреждённые элементы (если есть).
4) environment: опиши условия съёмки (погода, освещённость, блики/влажность).

ОЦЕНКИ И ПРАВИЛА
- Если уверенность низкая: понижай confidence, ставь "uncertain": true и пиши краткую причину в notes.
- Если несколько машин: оцени ближайшую/центральную, добавь в notes: "multiple_cars".
- Не выдумывай координаты. Если не уверен в bbox, оставь null/не указывай bbox.
- Процент бликов/влажности оценивай грубо (0.0–1.0).
- Не добавляй ключей вне схемы. Верни ТОЛЬКО JSON.

ПЕРЕЧНИ (используй только эти значения)
- damage_details.parts[].part:
  ["bumper_front","bumper_rear","fender_left","fender_right",
   "door_left_front","door_left_rear","door_right_front","door_right_rear",
   "hood","trunk","headlight_left","headlight_right","taillight_left","taillight_right",
   "mirror_left","mirror_right","windshield","side_window_left","side_window_right",
   "wheel_left_front","wheel_right_front","wheel_left_rear","wheel_right_rear",
   "roof","sill_left","sill_right"]
- damage_details.parts[].type:
  ["scratch","dent","crack","broken_glass","paint_peel","rust","misalignment","missing_part","other"]
  Если "other" — заполни other_desc (кратко).
- damage_details.parts[].bbox: ОБЯЗАТЕЛЬНО указывай координаты повреждения в формате [x1,y1,x2,y2] 
  где x1,y1 - левый верхний угол, x2,y2 - правый нижний угол (нормализованные 0-1).
  КРИТИЧЕСКИ ВАЖНО: Для КАЖДОГО повреждения указывай точные координаты bbox!
- environment.weather:
  ["sunny","cloudy","rain","snow","fog","night","indoor","unknown"]
- environment.lighting:
  ["normal","low_light","strong_glare","backlight","mixed","artificial"]

ТРЕБОВАНИЯ К ЧИСЛАМ
- Все confidence в диапазоне [0,1], три знака после запятой.
- glare_coverage_pct и wetness_pct — 0.0..1.0.

СТРОГАЯ СХЕМА ОТВЕТА:
{
  "integrity": {
    "label": "damaged|undamaged",
    "confidence": 0.000
  },
  "cleanliness": {
    "label": "clean|slightly_dirty|dirty",
    "confidence": 0.000
  },
  "damage_details": {
    "overall_confidence": 0.000,
    "parts": [
      {
        "part": "hood",
        "type": "scratch",
        "confidence": 0.000,
        "bbox": [0.12, 0.25, 0.58, 0.47]
      }
    ]
  },
  "environment": {
    "weather": "sunny",
    "lighting": "strong_glare",
    "glare_coverage_pct": 0.15,
    "wet_surface": false,
    "wetness_pct": 0.00,
    "raindrops_visible": false,
    "reflections_strong": true,
    "confidence": 0.000
  },
  "uncertain": false,
  "notes": ""
}

ПАМЯТКА ПО ИНТЕРПРЕТАЦИИ
- "dirty": заметная грязь/налёт/брызги (>5% площади кузова).
- "slightly_dirty": лёгкая грязь/локальные пятна (≈1–5%).
- "clean": почти без грязи (<1%).
- Если ночь/сильная засветка/полмашины вне кадра — ставь uncertain=true и укажи причину в notes.
Ни при каких условиях не добавляй ничего, кроме указанного JSON."""
    
    def _parse_response(self, raw_text: str) -> Dict[str, Any]:
        """Парсит ответ от Gemini"""
        try:
            # Извлекаем JSON из markdown блока
            if raw_text.startswith('```json'):
                match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
                if match:
                    json_text = match.group(1).strip()
                else:
                    json_text = raw_text[7:].strip()
            elif raw_text.startswith('```'):
                match = re.search(r'```\s*(.*?)\s*```', raw_text, re.DOTALL)
                if match:
                    json_text = match.group(1).strip()
                else:
                    json_text = raw_text[3:].strip()
            else:
                json_text = raw_text
            
            # Парсим JSON
            import json
            return json.loads(json_text)
            
        except Exception as e:
            return {
                'error': f'Failed to parse response: {str(e)}',
                'integrity': {'label': 'unknown', 'confidence': 0.0},
                'cleanliness': {'label': 'unknown', 'confidence': 0.0},
                'damage_details': {'parts': []},
                'environment': {},
                'uncertain': True,
                'notes': f'Parse error: {str(e)}'
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели"""
        return {
            'available': self.available,
            'gemini_available': GEMINI_AVAILABLE,
            'model_name': self.model_name,
            'api_key_set': bool(self.api_key)
        }
