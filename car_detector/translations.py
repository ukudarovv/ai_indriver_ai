# Словари переводов для частей автомобиля и типов повреждений

# Переводы частей автомобиля
CAR_PARTS_TRANSLATIONS = {
    "bumper_front": "Передний бампер",
    "bumper_rear": "Задний бампер", 
    "fender_left": "Левое крыло",
    "fender_right": "Правое крыло",
    "door_left_front": "Левая передняя дверь",
    "door_left_rear": "Левая задняя дверь",
    "door_right_front": "Правая передняя дверь",
    "door_right_rear": "Правая задняя дверь",
    "hood": "Капот",
    "trunk": "Багажник",
    "headlight_left": "Левая фара",
    "headlight_right": "Правая фара",
    "taillight_left": "Левый задний фонарь",
    "taillight_right": "Правый задний фонарь",
    "mirror_left": "Левое зеркало",
    "mirror_right": "Правое зеркало",
    "windshield": "Лобовое стекло",
    "side_window_left": "Левое боковое стекло",
    "side_window_right": "Правое боковое стекло",
    "wheel_left_front": "Левое переднее колесо",
    "wheel_right_front": "Правое переднее колесо",
    "wheel_left_rear": "Левое заднее колесо",
    "wheel_right_rear": "Правое заднее колесо",
    "roof": "Крыша",
    "sill_left": "Левый порог",
    "sill_right": "Правый порог"
}

# Переводы типов повреждений
DAMAGE_TYPES_TRANSLATIONS = {
    "scratch": "Царапина",
    "dent": "Вмятина",
    "crack": "Трещина",
    "broken_glass": "Разбитое стекло",
    "paint_peel": "Отслоение краски",
    "rust": "Ржавчина",
    "misalignment": "Перекос",
    "missing_part": "Отсутствующая деталь",
    "other": "Другое"
}

# Переводы состояний целостности
INTEGRITY_TRANSLATIONS = {
    "damaged": "Поврежден",
    "undamaged": "Без повреждений"
}

# Переводы состояний чистоты
CLEANLINESS_TRANSLATIONS = {
    "clean": "Чистый",
    "slightly_dirty": "Слегка грязный",
    "dirty": "Грязный"
}

# Переводы погодных условий
WEATHER_TRANSLATIONS = {
    "sunny": "Солнечно",
    "cloudy": "Облачно",
    "rain": "Дождь",
    "snow": "Снег",
    "fog": "Туман",
    "night": "Ночь",
    "indoor": "В помещении",
    "unknown": "Неизвестно"
}

# Переводы освещения
LIGHTING_TRANSLATIONS = {
    "normal": "Нормальное",
    "low_light": "Слабое освещение",
    "strong_glare": "Сильные блики",
    "backlight": "Контровый свет",
    "mixed": "Смешанное",
    "artificial": "Искусственное"
}

def translate_car_part(part):
    """Переводит название части автомобиля на русский"""
    return CAR_PARTS_TRANSLATIONS.get(part, part)

def translate_damage_type(damage_type):
    """Переводит тип повреждения на русский"""
    return DAMAGE_TYPES_TRANSLATIONS.get(damage_type, damage_type)

def translate_integrity(integrity):
    """Переводит состояние целостности на русский"""
    return INTEGRITY_TRANSLATIONS.get(integrity, integrity)

def translate_cleanliness(cleanliness):
    """Переводит состояние чистоты на русский"""
    return CLEANLINESS_TRANSLATIONS.get(cleanliness, cleanliness)

def translate_weather(weather):
    """Переводит погодные условия на русский"""
    return WEATHER_TRANSLATIONS.get(weather, weather)

def translate_lighting(lighting):
    """Переводит освещение на русский"""
    return LIGHTING_TRANSLATIONS.get(lighting, lighting)
