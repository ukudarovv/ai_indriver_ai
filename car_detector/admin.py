from django.contrib import admin
from .models import CarAnalysis


@admin.register(CarAnalysis)
class CarAnalysisAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'created_at', 'gemini_integrity_label', 
        'gemini_cleanliness_label', 'gemini_damage_count', 
        'yolo_detection_count', 'processing_time'
    ]
    list_filter = [
        'gemini_integrity_label', 'gemini_cleanliness_label', 
        'gemini_uncertain', 'created_at'
    ]
    search_fields = ['gemini_notes']
    readonly_fields = [
        'created_at', 'processing_time', 'gemini_damage_count', 
        'yolo_detection_count'
    ]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('image', 'created_at', 'processing_time')
        }),
        ('Gemini анализ', {
            'fields': (
                'gemini_integrity_label', 'gemini_integrity_confidence',
                'gemini_cleanliness_label', 'gemini_cleanliness_confidence',
                'gemini_damage_details', 'gemini_environment',
                'gemini_uncertain', 'gemini_notes'
            )
        }),
        ('YOLO анализ', {
            'fields': ('yolo_detections', 'yolo_confidence')
        }),
        ('Статистика', {
            'fields': ('gemini_damage_count', 'yolo_detection_count'),
            'classes': ('collapse',)
        })
    )
