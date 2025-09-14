from django.db import models
from django.utils import timezone
import json


class CarAnalysis(models.Model):
    """Модель для хранения результатов анализа автомобиля"""
    
    # Основная информация
    image = models.ImageField(upload_to='car_images/')
    processed_image = models.ImageField(upload_to='processed_images/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Результаты Gemini анализа
    gemini_integrity_label = models.CharField(max_length=20, choices=[
        ('damaged', 'Damaged'),
        ('undamaged', 'Undamaged'),
    ])
    gemini_integrity_confidence = models.FloatField()
    
    gemini_cleanliness_label = models.CharField(max_length=20, choices=[
        ('clean', 'Clean'),
        ('slightly_dirty', 'Slightly Dirty'),
        ('dirty', 'Dirty'),
    ])
    gemini_cleanliness_confidence = models.FloatField()
    
    # Детали повреждений (JSON)
    gemini_damage_details = models.JSONField(default=dict)
    
    # Условия съемки (JSON)
    gemini_environment = models.JSONField(default=dict)
    
    gemini_uncertain = models.BooleanField(default=False)
    gemini_notes = models.TextField(blank=True)
    
    # Результаты YOLO анализа
    yolo_detections = models.JSONField(default=list)  # Список обнаруженных объектов
    yolo_confidence = models.FloatField(null=True, blank=True)
    
    # Общие поля
    processing_time = models.FloatField(null=True, blank=True)  # Время обработки в секундах
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Car Analysis'
        verbose_name_plural = 'Car Analyses'
    
    def __str__(self):
        return f"Analysis {self.id} - {self.gemini_integrity_label} ({self.created_at.strftime('%Y-%m-%d %H:%M')})"
    
    @property
    def gemini_damage_count(self):
        """Количество обнаруженных повреждений"""
        if self.gemini_damage_details and 'parts' in self.gemini_damage_details:
            return len(self.gemini_damage_details['parts'])
        return 0
    
    @property
    def yolo_detection_count(self):
        """Количество обнаруженных объектов YOLO"""
        return len(self.yolo_detections) if self.yolo_detections else 0
