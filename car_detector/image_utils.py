import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
from typing import List, Dict, Tuple, Optional

def draw_damage_boxes(image_path: str, damage_parts: List[Dict], output_path: str) -> str:
    """
    Рисует прямоугольники повреждений на изображении
    
    Args:
        image_path: Путь к исходному изображению
        damage_parts: Список повреждений с координатами bbox
        output_path: Путь для сохранения результата
    
    Returns:
        Путь к обработанному изображению
    """
    try:
        # Загружаем изображение
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")
        
        height, width = image.shape[:2]
        
        # Цвета для разных типов повреждений (BGR формат для OpenCV)
        damage_colors = {
            'scratch': (0, 255, 255),    # Желтый
            'dent': (0, 0, 255),         # Красный
            'crack': (255, 0, 0),        # Синий
            'broken_glass': (0, 255, 0), # Зеленый
            'paint_peel': (255, 0, 255), # Пурпурный
            'rust': (128, 0, 128),       # Фиолетовый
            'misalignment': (0, 165, 255), # Оранжевый
            'missing_part': (128, 128, 128), # Серый
            'other': (0, 255, 255)       # Голубой
        }
        
        # Рисуем прямоугольники для каждого повреждения
        for part in damage_parts:
            if 'bbox' in part and part['bbox']:
                bbox = part['bbox']
                if len(bbox) == 4:
                    # Конвертируем нормализованные координаты в пиксели
                    x1 = int(bbox[0] * width)
                    y1 = int(bbox[1] * height)
                    x2 = int(bbox[2] * width)
                    y2 = int(bbox[3] * height)
                    
                    # Получаем цвет для типа повреждения
                    damage_type = part.get('type', 'other')
                    color = damage_colors.get(damage_type, (255, 255, 255))
                    
                    # Рисуем толстый прямоугольник
                    cv2.rectangle(image, (x1, y1), (x2, y2), color, 5)
                    
                    # Добавляем текст с типом повреждения (на английском)
                    label = f"{damage_type} ({part.get('confidence', 0):.1%})"
                    font_scale = 0.8
                    thickness = 2
                    
                    print(f"Рисуем повреждение: {damage_type} в координатах ({x1},{y1})-({x2},{y2}) цветом {color}")
                    
                    # Получаем размер текста
                    (text_width, text_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
                    )
                    
                    # Рисуем фон для текста
                    cv2.rectangle(
                        image, 
                        (x1, y1 - text_height - 10), 
                        (x1 + text_width, y1), 
                        color, 
                        -1
                    )
                    
                    # Рисуем текст
                    cv2.putText(
                        image, 
                        label, 
                        (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        font_scale, 
                        (255, 255, 255), 
                        thickness
                    )
        
        # Сохраняем результат
        cv2.imwrite(output_path, image)
        return output_path
        
    except Exception as e:
        print(f"Ошибка при рисовании повреждений: {e}")
        # Возвращаем исходное изображение в случае ошибки
        return image_path

def draw_yolo_detections(image_path: str, detections: List[Dict], output_path: str) -> str:
    """
    Рисует детекции YOLO на изображении
    
    Args:
        image_path: Путь к исходному изображению
        detections: Список детекций YOLO
        output_path: Путь для сохранения результата
    
    Returns:
        Путь к обработанному изображению
    """
    try:
        # Загружаем изображение
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {image_path}")
        
        height, width = image.shape[:2]
        
        # Цвет для YOLO детекций (зеленый)
        yolo_color = (0, 255, 0)
        
        # Рисуем прямоугольники для каждой детекции
        for detection in detections:
            if 'bbox' in detection and detection['bbox']:
                bbox = detection['bbox']
                if len(bbox) == 4:
                    # Конвертируем нормализованные координаты в пиксели
                    x1 = int(bbox[0] * width)
                    y1 = int(bbox[1] * height)
                    x2 = int(bbox[2] * width)
                    y2 = int(bbox[3] * height)
                    
                    # Рисуем толстый прямоугольник
                    cv2.rectangle(image, (x1, y1), (x2, y2), yolo_color, 5)
                    
                    # Добавляем текст с классом и уверенностью
                    label = f"YOLO: {detection.get('class', 'unknown')} ({detection.get('confidence', 0):.1%})"
                    font_scale = 0.7
                    thickness = 2
                    
                    # Получаем размер текста
                    (text_width, text_height), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
                    )
                    
                    # Рисуем фон для текста
                    cv2.rectangle(
                        image, 
                        (x1, y1 - text_height - 10), 
                        (x1 + text_width, y1), 
                        yolo_color, 
                        -1
                    )
                    
                    # Рисуем текст
                    cv2.putText(
                        image, 
                        label, 
                        (x1, y1 - 5), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        font_scale, 
                        (255, 255, 255), 
                        thickness
                    )
        
        # Сохраняем результат
        cv2.imwrite(output_path, image)
        return output_path
        
    except Exception as e:
        print(f"Ошибка при рисовании YOLO детекций: {e}")
        # Возвращаем исходное изображение в случае ошибки
        return image_path

def create_comparison_image(original_path: str, gemini_damages: List[Dict], 
                          yolo_detections: List[Dict], output_path: str) -> str:
    """
    Создает изображение с наложенными повреждениями от обеих моделей
    
    Args:
        original_path: Путь к исходному изображению
        gemini_damages: Список повреждений от Gemini
        yolo_detections: Список детекций от YOLO
        output_path: Путь для сохранения результата
    
    Returns:
        Путь к обработанному изображению
    """
    try:
        # Загружаем изображение
        image = cv2.imread(original_path)
        if image is None:
            raise ValueError(f"Не удалось загрузить изображение: {original_path}")
        
        height, width = image.shape[:2]
        print(f"Создаем сравнение изображения размером {width}x{height}")
        print(f"Gemini повреждений: {len(gemini_damages)}")
        print(f"YOLO детекций: {len(yolo_detections)}")
        
        # Цвета для разных моделей
        gemini_color = (0, 0, 255)  # Красный для Gemini
        yolo_color = (0, 255, 0)    # Зеленый для YOLO
        
        # Рисуем повреждения Gemini
        for part in gemini_damages:
            if 'bbox' in part and part['bbox']:
                bbox = part['bbox']
                if len(bbox) == 4:
                    x1 = int(bbox[0] * width)
                    y1 = int(bbox[1] * height)
                    x2 = int(bbox[2] * width)
                    y2 = int(bbox[3] * height)
                    
                    # Рисуем толстый пунктирный прямоугольник для Gemini
                    draw_dashed_rectangle(image, (x1, y1), (x2, y2), gemini_color, 5)
                    
                    # Добавляем текст (используем только английские символы)
                    damage_type = part.get('type', 'damage')
                    label = f"Gemini: {damage_type}"
                    cv2.putText(
                        image, label, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, gemini_color, 3
                    )
                    
                    print(f"Рисуем Gemini повреждение: {part.get('type', 'damage')} в координатах ({x1},{y1})-({x2},{y2})")
        
        # Рисуем детекции YOLO
        for detection in yolo_detections:
            if 'bbox' in detection and detection['bbox']:
                bbox = detection['bbox']
                if len(bbox) == 4:
                    x1 = int(bbox[0] * width)
                    y1 = int(bbox[1] * height)
                    x2 = int(bbox[2] * width)
                    y2 = int(bbox[3] * height)
                    
                    # Рисуем толстый сплошной прямоугольник для YOLO
                    cv2.rectangle(image, (x1, y1), (x2, y2), yolo_color, 5)
                    
                    # Добавляем текст (используем только английские символы)
                    class_name = detection.get('class', 'detection')
                    label = f"YOLO: {class_name}"
                    cv2.putText(
                        image, label, (x1, y2 + 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, yolo_color, 3
                    )
                    
                    print(f"Рисуем YOLO детекцию: {detection.get('class', 'detection')} в координатах ({x1},{y1})-({x2},{y2})")
        
        # Добавляем легенду (на английском для совместимости с OpenCV)
        legend_y = 30
        cv2.putText(image, "Gemini (red dashed)", (10, legend_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, gemini_color, 2)
        cv2.putText(image, "YOLO (green solid)", (10, legend_y + 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, yolo_color, 2)
        
        # Сохраняем результат
        cv2.imwrite(output_path, image)
        return output_path
        
    except Exception as e:
        print(f"Ошибка при создании сравнения: {e}")
        return original_path

def draw_dashed_rectangle(image, pt1, pt2, color, thickness):
    """Рисует пунктирный прямоугольник"""
    x1, y1 = pt1
    x2, y2 = pt2
    
    # Рисуем пунктирные линии
    dash_length = 10
    gap_length = 5
    
    # Верхняя линия
    draw_dashed_line(image, (x1, y1), (x2, y1), color, thickness, dash_length, gap_length)
    # Нижняя линия
    draw_dashed_line(image, (x1, y2), (x2, y2), color, thickness, dash_length, gap_length)
    # Левая линия
    draw_dashed_line(image, (x1, y1), (x1, y2), color, thickness, dash_length, gap_length)
    # Правая линия
    draw_dashed_line(image, (x2, y1), (x2, y2), color, thickness, dash_length, gap_length)

def draw_dashed_line(image, pt1, pt2, color, thickness, dash_length, gap_length):
    """Рисует пунктирную линию"""
    x1, y1 = pt1
    x2, y2 = pt2
    
    # Вычисляем длину линии
    length = np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    # Вычисляем количество сегментов
    num_segments = int(length / (dash_length + gap_length))
    
    # Вычисляем шаг
    dx = (x2 - x1) / num_segments
    dy = (y2 - y1) / num_segments
    
    # Рисуем сегменты
    for i in range(num_segments):
        start_x = int(x1 + i * dx)
        start_y = int(y1 + i * dy)
        end_x = int(x1 + (i + dash_length / (dash_length + gap_length)) * dx)
        end_y = int(y1 + (i + dash_length / (dash_length + gap_length)) * dy)
        
        cv2.line(image, (start_x, start_y), (end_x, end_y), color, thickness)
