# car_detector/models_ai/yolo_detector.py
import os
import math
from typing import List, Dict, Any
from PIL import Image
import numpy as np

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("Warning: ultralytics not available. YOLO detection will be disabled.")


class YOLODetector:
    """YOLO детектор для обнаружения повреждений автомобилей"""
    
    def __init__(self, weights_path: str = None):
        self.model = None
        self.class_labels = [
            'Bodypanel-Dent', 'Front-Windscreen-Damage', 'Headlight-Damage', 
            'Rear-windscreen-Damage', 'RunningBoard-Dent', 'Sidemirror-Damage', 
            'Signlight-Damage', 'Taillight-Damage', 'bonnet-dent', 'boot-dent', 
            'doorouter-dent', 'fender-dent', 'front-bumper-dent', 'pillar-dent', 
            'quaterpanel-dent', 'rear-bumper-dent', 'roof-dent'
        ]
        
        if YOLO_AVAILABLE and weights_path and os.path.exists(weights_path):
            try:
                self.model = YOLO(weights_path)
                print(f"YOLO model loaded from {weights_path}")
            except Exception as e:
                print(f"Error loading YOLO model: {e}")
                self.model = None
        else:
            print("YOLO model not available")
    
    def detect(self, image: Image.Image, confidence_threshold: float = 0.3) -> List[Dict[str, Any]]:
        """
        Обнаруживает повреждения на изображении
        
        Args:
            image: PIL Image объект
            confidence_threshold: Минимальный порог уверенности
            
        Returns:
            Список обнаруженных повреждений
        """
        if not self.model:
            return []
        
        try:
            # Конвертируем PIL в numpy array для YOLO
            img_array = np.array(image)
            
            # Выполняем детекцию
            results = self.model(img_array)
            
            detections = []
            
            # Обрабатываем результаты
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for box in boxes:
                        # Координаты bounding box
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                        
                        # Уверенность и класс
                        conf = float(box.conf[0].cpu().numpy())
                        cls = int(box.cls[0].cpu().numpy())
                        
                        if conf >= confidence_threshold:
                            # Нормализуем координаты (0-1)
                            img_width, img_height = image.size
                            normalized_bbox = [
                                x1 / img_width,
                                y1 / img_height,
                                x2 / img_width,
                                y2 / img_height
                            ]
                            
                            detection = {
                                'class': self.class_labels[cls] if cls < len(self.class_labels) else f'class_{cls}',
                                'confidence': conf,
                                'bbox': normalized_bbox,
                                'bbox_pixels': [x1, y1, x2, y2],
                                'area': (x2 - x1) * (y2 - y1)
                            }
                            detections.append(detection)
            
            return detections
            
        except Exception as e:
            print(f"Error during YOLO detection: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """Возвращает информацию о модели"""
        return {
            'available': self.model is not None,
            'yolo_available': YOLO_AVAILABLE,
            'class_count': len(self.class_labels),
            'classes': self.class_labels
        }
