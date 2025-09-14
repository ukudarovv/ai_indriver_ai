# gemini_car_state.py
import os
import io
import json
import argparse
import re
from typing import Literal, Optional, List

from pydantic import BaseModel, Field
from PIL import Image

# Google Gemini SDK (google-generativeai)
import google.generativeai as genai


# ──────────────────────────────────────────────────────────────────────────────
# 1) Промпт
# ──────────────────────────────────────────────────────────────────────────────
PROMPT = """Ты — строгий визуальный аудитор фото автомобиля. На вход ОДНО фото.
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
Ни при каких условиях не добавляй ничего, кроме указанного JSON.
"""


# ──────────────────────────────────────────────────────────────────────────────
# 2) Pydantic-схема ожидаемого JSON (для строгого ответа)
# ──────────────────────────────────────────────────────────────────────────────
class Cleanliness(BaseModel):
    label: Literal["clean","slightly_dirty","dirty"]
    confidence: float = Field(ge=0.0, le=1.0)

class Integrity(BaseModel):
    label: Literal["damaged","undamaged"]
    confidence: float = Field(ge=0.0, le=1.0)

class DamageItem(BaseModel):
    part: Literal[
        "bumper_front","bumper_rear","fender_left","fender_right",
        "door_left_front","door_left_rear","door_right_front","door_right_rear",
        "hood","trunk","headlight_left","headlight_right","taillight_left","taillight_right",
        "mirror_left","mirror_right","windshield","side_window_left","side_window_right",
        "wheel_left_front","wheel_right_front","wheel_left_rear","wheel_right_rear",
        "roof","sill_left","sill_right"
    ]
    type: Literal[
        "scratch","dent","crack","broken_glass","paint_peel","rust","misalignment","missing_part","other"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    bbox: Optional[list[float]] = None  # [x1,y1,x2,y2] в 0..1, можно опустить
    other_desc: Optional[str] = None    # обязательно, если type == "other"

class DamageDetails(BaseModel):
    overall_confidence: float = Field(ge=0.0, le=1.0)
    parts: List[DamageItem] = []

class Environment(BaseModel):
    weather: Literal["sunny","cloudy","rain","snow","fog","night","indoor","unknown"]
    lighting: Literal["normal","low_light","strong_glare","backlight","mixed","artificial"]
    glare_coverage_pct: float = Field(ge=0.0, le=1.0)
    wet_surface: bool
    wetness_pct: float = Field(ge=0.0, le=1.0)
    raindrops_visible: bool
    reflections_strong: bool
    confidence: float = Field(ge=0.0, le=1.0)

class ResultV2(BaseModel):
    integrity: Integrity
    cleanliness: Cleanliness
    damage_details: DamageDetails
    environment: Environment
    uncertain: bool = False
    notes: Optional[str] = ""


# ──────────────────────────────────────────────────────────────────────────────
# 3) Вспомогательное: грузим картинку и нормализуем в JPEG-байты
# ──────────────────────────────────────────────────────────────────────────────
def load_as_jpeg_bytes(image_path: str, quality: int = 92) -> bytes:
    """
    Открывает любое поддерживаемое PIL изображение и кодирует его в JPEG-байты.
    Это делает поведение стабильным для PNG/WEBP/HEIC и т.п.
    """
    with Image.open(image_path) as im:
        im = im.convert("RGB")
        buf = io.BytesIO()
        im.save(buf, format="JPEG", quality=quality)
        return buf.getvalue()


# ──────────────────────────────────────────────────────────────────────────────
# 4) Основная функция классификации
# ──────────────────────────────────────────────────────────────────────────────
def classify_with_gemini(
    image_path: str,
    model: str = "gemini-1.5-flash",
) -> dict:
    """
    Классифицирует одно фото по детальным параметрам: integrity, cleanliness, 
    damage_details и environment.
    Возвращает dict, соответствующий схеме ResultV2.
    Требуется переменная окружения GEMINI_API_KEY.
    """
    # 4.1 Проверяем API-ключ
    api_key = "AIzaSyBcHZOH8nT045oOgdefL3iNOyJc0n0jgfQ"
    if not api_key:
        raise RuntimeError(
            "Не найден GEMINI_API_KEY в окружении. "
            "Установите командой: setx GEMINI_API_KEY \"<ключ>\" (Windows) "
            "или export GEMINI_API_KEY=\"<ключ>\" (Linux/Mac) и перезапустите терминал."
        )

    # 4.2 Настраиваем API
    genai.configure(api_key=api_key)

    # 4.3 Грузим и конвертируем изображение в JPEG-байты
    image_bytes = load_as_jpeg_bytes(image_path)

    # 4.4 Создаем модель
    model_instance = genai.GenerativeModel(model)

    # 4.5 Вызываем модель с изображением и промптом
    response = model_instance.generate_content([
        {
            "mime_type": "image/jpeg",
            "data": image_bytes
        },
        PROMPT
    ])

    # 4.6 Забираем JSON и валидируем pydantic-ом (гарантия формата)
    raw_text = response.text  # SDK отдаёт текст ответа (ожидаем чистый JSON)
    # Если хотите увидеть «как пришло»: print(raw_text)
    
    # Извлекаем JSON из markdown блока если нужно
    if raw_text.startswith('```json'):
        # Используем регулярное выражение для извлечения JSON
        match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
        if match:
            json_text = match.group(1).strip()
        else:
            json_text = raw_text[7:].strip()
    elif raw_text.startswith('```'):
        # Используем регулярное выражение для извлечения JSON
        match = re.search(r'```\s*(.*?)\s*```', raw_text, re.DOTALL)
        if match:
            json_text = match.group(1).strip()
        else:
            json_text = raw_text[3:].strip()
    else:
        json_text = raw_text
    
    parsed = ResultV2.model_validate_json(json_text).model_dump()
    return parsed


# ──────────────────────────────────────────────────────────────────────────────
# 5) CLI: python gemini_car_state.py --image "C:\path\car.jpg" [--model ...]
# ──────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Классификация состояния авто (Gemini). Возвращает JSON."
    )
    parser.add_argument(
        "--image", "-i",
        required=True,
        help="Путь к файлу изображения (любого поддерживаемого формата)."
    )
    parser.add_argument(
        "--model", "-m",
        default="gemini-1.5-flash",
        help="ID модели Gemini (по умолчанию: gemini-1.5-flash)."
    )
    args = parser.parse_args()

    result = classify_with_gemini(args.image, model=args.model)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
