# car_detector/services.py
import os
import time
import json
from typing import Dict, List, Any
from PIL import Image
import io
from django.core.files.base import ContentFile

# Импорты интегрированных моделей
from .models_ai import YOLODetector, GeminiAnalyzer
from .image_utils import create_comparison_image


class CarAnalysisService:
    """Сервис для анализа автомобилей с использованием Gemini и YOLO"""
    
    def __init__(self):
        # Инициализируем модели
        self.gemini_analyzer = GeminiAnalyzer()
        self.yolo_detector = None
        self._init_yolo()
    
    def _init_yolo(self):
        """Инициализация YOLO детектора"""
        try:
            # Ищем веса модели
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            weights_path = os.path.join(base_dir, "CarDentDetector", "Weights", "best.pt")
            
            if os.path.exists(weights_path):
                self.yolo_detector = YOLODetector(weights_path)
                print("YOLO detector initialized successfully")
            else:
                print(f"YOLO weights not found at {weights_path}")
                self.yolo_detector = YOLODetector()  # Создаем без весов
        except Exception as e:
            print(f"Error initializing YOLO detector: {e}")
            self.yolo_detector = YOLODetector()  # Создаем без весов
    
    def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """
        Анализирует изображение автомобиля с помощью обеих моделей
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Словарь с результатами анализа
        """
        start_time = time.time()
        results = {
            'gemini': None,
            'yolo': None,
            'processing_time': 0,
            'errors': []
        }
        
        # Анализ с помощью Gemini
        try:
            print("Running Gemini analysis...")
            gemini_results = self.gemini_analyzer.analyze(image_path)
            results['gemini'] = gemini_results
            print("Gemini analysis completed")
        except Exception as e:
            error_msg = f"Gemini analysis failed: {str(e)}"
            print(error_msg)
            results['errors'].append(error_msg)
        
        # Анализ с помощью YOLO
        try:
            if self.yolo_detector:
                print("Running YOLO analysis...")
                yolo_results = self._run_yolo_analysis(image_path)
                results['yolo'] = yolo_results
                print("YOLO analysis completed")
            else:
                results['errors'].append("YOLO detector not available")
        except Exception as e:
            error_msg = f"YOLO analysis failed: {str(e)}"
            print(error_msg)
            results['errors'].append(error_msg)
        
        # Вычисляем время обработки
        results['processing_time'] = time.time() - start_time
        
        return results
    
    def create_processed_image(self, image_path: str, gemini_results: Dict, yolo_results: Dict) -> str:
        """
        Создает обработанное изображение с наложенными повреждениями
        
        Args:
            image_path: Путь к исходному изображению
            gemini_results: Результаты Gemini анализа
            yolo_results: Результаты YOLO анализа
            
        Returns:
            Путь к обработанному изображению
        """
        try:
            # Извлекаем повреждения из результатов Gemini
            gemini_damages = []
            if 'damage_details' in gemini_results and 'parts' in gemini_results['damage_details']:
                gemini_damages = gemini_results['damage_details']['parts']
                print(f"Найдено {len(gemini_damages)} повреждений Gemini")
                for i, damage in enumerate(gemini_damages):
                    print(f"  Повреждение {i+1}: {damage.get('part', 'unknown')} - {damage.get('type', 'unknown')}")
                    if 'bbox' in damage:
                        print(f"    Координаты: {damage['bbox']}")
                    else:
                        print(f"    Координаты: НЕТ!")
            
            # Извлекаем детекции из результатов YOLO
            yolo_detections = []
            if 'detections' in yolo_results:
                yolo_detections = yolo_results['detections']
                print(f"Найдено {len(yolo_detections)} детекций YOLO")
                for i, detection in enumerate(yolo_detections):
                    print(f"  Детекция {i+1}: {detection.get('class', 'unknown')}")
                    if 'bbox' in detection:
                        print(f"    Координаты: {detection['bbox']}")
                    else:
                        print(f"    Координаты: НЕТ!")
            
            # Создаем временный файл для обработанного изображения
            temp_dir = os.path.dirname(image_path)
            temp_filename = f"processed_{os.path.basename(image_path)}"
            temp_path = os.path.join(temp_dir, temp_filename)
            
            # Создаем обработанное изображение
            processed_path = create_comparison_image(
                image_path, gemini_damages, yolo_detections, temp_path
            )
            
            return processed_path
            
        except Exception as e:
            print(f"Ошибка при создании обработанного изображения: {e}")
            return image_path
    
    def _run_yolo_analysis(self, image_path: str) -> Dict[str, Any]:
        """
        Запускает анализ с помощью YOLO
        
        Args:
            image_path: Путь к изображению
            
        Returns:
            Результаты YOLO анализа
        """
        try:
            # Проверяем, инициализирован ли детектор
            if not self.yolo_detector or not self.yolo_detector.model:
                return {
                    'detections': [],
                    'total_detections': 0,
                    'confidence_scores': [],
                    'average_confidence': 0.0,
                    'error': 'YOLO detector not available'
                }
            
            # Загружаем изображение
            image = Image.open(image_path)
            
            # Запускаем детекцию
            detections = self.yolo_detector.detect(image)
            
            # Форматируем результаты
            yolo_results = {
                'detections': [],
                'total_detections': len(detections),
                'confidence_scores': []
            }
            
            for detection in detections:
                detection_data = {
                    'class': detection.get('class', 'unknown'),
                    'confidence': detection.get('confidence', 0.0),
                    'bbox': detection.get('bbox', []),
                    'bbox_pixels': detection.get('bbox_pixels', []),
                    'area': detection.get('area', 0)
                }
                yolo_results['detections'].append(detection_data)
                yolo_results['confidence_scores'].append(detection.get('confidence', 0.0))
            
            # Вычисляем среднюю уверенность
            if yolo_results['confidence_scores']:
                yolo_results['average_confidence'] = sum(yolo_results['confidence_scores']) / len(yolo_results['confidence_scores'])
            else:
                yolo_results['average_confidence'] = 0.0
            
            return yolo_results
            
        except Exception as e:
            return {
                'detections': [],
                'total_detections': 0,
                'confidence_scores': [],
                'average_confidence': 0.0,
                'error': f"YOLO analysis error: {str(e)}"
            }
    
    def format_results_for_django(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Форматирует результаты анализа для сохранения в Django модели
        
        Args:
            analysis_results: Результаты анализа от analyze_image
            
        Returns:
            Форматированные данные для Django модели
        """
        # Устанавливаем значения по умолчанию для всех обязательных полей
        formatted_data = {
            'gemini_integrity_label': 'undamaged',
            'gemini_integrity_confidence': 0.0,
            'gemini_cleanliness_label': 'clean',
            'gemini_cleanliness_confidence': 0.0,
            'gemini_damage_details': {},
            'gemini_environment': {},
            'gemini_uncertain': False,
            'gemini_notes': '',
            'yolo_detections': [],
            'yolo_confidence': 0.0,
        }
        
        # Обрабатываем результаты Gemini
        if analysis_results.get('gemini'):
            gemini = analysis_results['gemini']
            
            formatted_data.update({
                'gemini_integrity_label': gemini.get('integrity', {}).get('label', 'undamaged'),
                'gemini_integrity_confidence': gemini.get('integrity', {}).get('confidence', 0.0),
                'gemini_cleanliness_label': gemini.get('cleanliness', {}).get('label', 'clean'),
                'gemini_cleanliness_confidence': gemini.get('cleanliness', {}).get('confidence', 0.0),
                'gemini_damage_details': gemini.get('damage_details', {}),
                'gemini_environment': gemini.get('environment', {}),
                'gemini_uncertain': gemini.get('uncertain', False),
                'gemini_notes': gemini.get('notes', ''),
            })
        
        # Обрабатываем результаты YOLO
        if analysis_results.get('yolo'):
            yolo = analysis_results['yolo']
            
            formatted_data.update({
                'yolo_detections': yolo.get('detections', []),
                'yolo_confidence': yolo.get('average_confidence', 0.0),
            })
        
        # Добавляем время обработки
        formatted_data['processing_time'] = analysis_results.get('processing_time', 0.0)
        
        return formatted_data


# Глобальный экземпляр сервиса
car_analysis_service = CarAnalysisService()
