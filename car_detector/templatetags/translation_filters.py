from django import template
from ..translations import (
    translate_car_part, translate_damage_type, translate_integrity,
    translate_cleanliness, translate_weather, translate_lighting
)

register = template.Library()

@register.filter
def mul(value, arg):
    """Умножает значение на аргумент"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def translate_car_part_filter(part):
    """Фильтр для перевода частей автомобиля"""
    return translate_car_part(part)

@register.filter
def translate_damage_type_filter(damage_type):
    """Фильтр для перевода типов повреждений"""
    return translate_damage_type(damage_type)

@register.filter
def translate_integrity_filter(integrity):
    """Фильтр для перевода состояний целостности"""
    return translate_integrity(integrity)

@register.filter
def translate_cleanliness_filter(cleanliness):
    """Фильтр для перевода состояний чистоты"""
    return translate_cleanliness(cleanliness)

@register.filter
def translate_weather_filter(weather):
    """Фильтр для перевода погодных условий"""
    return translate_weather(weather)

@register.filter
def translate_lighting_filter(lighting):
    """Фильтр для перевода освещения"""
    return translate_lighting(lighting)
