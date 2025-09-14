from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import tempfile

from .models import CarAnalysis
from .services import car_analysis_service
from .translations import (
    translate_car_part, translate_damage_type, translate_integrity,
    translate_cleanliness, translate_weather, translate_lighting
)


def home(request):
    """Главная страница с формой загрузки изображения"""
    recent_analyses = CarAnalysis.objects.all()[:5]
    return render(request, 'car_detector/home.html', {
        'recent_analyses': recent_analyses
    })


def upload_and_analyze(request):
    """Обработка загрузки и анализа изображения"""
    if request.method == 'POST':
        if 'image' not in request.FILES:
            messages.error(request, 'Пожалуйста, выберите изображение')
            return redirect('dual_analysis')
        
        image_file = request.FILES['image']
        
        # Проверяем тип файла
        allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
        if image_file.content_type not in allowed_types:
            messages.error(request, 'Поддерживаются только изображения: JPEG, PNG, WebP')
            return redirect('dual_analysis')
        
        try:
            # Сохраняем изображение во временный файл
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                for chunk in image_file.chunks():
                    temp_file.write(chunk)
                temp_path = temp_file.name
            
            # Анализируем изображение
            analysis_results = car_analysis_service.analyze_image(temp_path)
            
            # Создаем запись в базе данных
            car_analysis = CarAnalysis()
            
            # Сбрасываем указатель файла в начало
            image_file.seek(0)
            car_analysis.image.save(
                image_file.name,
                ContentFile(image_file.read()),
                save=False
            )
            
            # Заполняем данные из результатов анализа
            formatted_data = car_analysis_service.format_results_for_django(analysis_results)
            for key, value in formatted_data.items():
                setattr(car_analysis, key, value)
            
            car_analysis.save()
            
            # Создаем обработанное изображение с наложенными повреждениями
            try:
                processed_path = car_analysis_service.create_processed_image(
                    temp_path, 
                    analysis_results.get('gemini', {}), 
                    analysis_results.get('yolo', {})
                )
                
                # Сохраняем обработанное изображение
                if processed_path != temp_path and os.path.exists(processed_path):
                    with open(processed_path, 'rb') as processed_file:
                        car_analysis.processed_image.save(
                            f"processed_{image_file.name}",
                            ContentFile(processed_file.read()),
                            save=True
                        )
                    # Удаляем временный обработанный файл
                    os.unlink(processed_path)
                    
            except Exception as e:
                print(f"Ошибка при создании обработанного изображения: {e}")
            
            # Удаляем временный файл
            os.unlink(temp_path)
            
            messages.success(request, 'Анализ завершен успешно!')
            return redirect('analysis_detail', analysis_id=car_analysis.id)
            
        except Exception as e:
            messages.error(request, f'Ошибка при анализе: {str(e)}')
            return redirect('dual_analysis')
    
    return redirect('dual_analysis')


def dual_analysis(request):
    """Страница для двойного анализа с Gemini и YOLO"""
    return render(request, 'car_detector/dual_analysis.html')


def analysis_detail(request, analysis_id):
    """Детальная страница с результатами анализа"""
    analysis = get_object_or_404(CarAnalysis, id=analysis_id)
    
    # Подготавливаем данные для шаблона
    context = {
        'analysis': analysis,
        'gemini_damage_parts': analysis.gemini_damage_details.get('parts', []),
        'yolo_detections': analysis.yolo_detections,
        'environment': analysis.gemini_environment,
        # Функции переводов
        'translate_car_part': translate_car_part,
        'translate_damage_type': translate_damage_type,
        'translate_integrity': translate_integrity,
        'translate_cleanliness': translate_cleanliness,
        'translate_weather': translate_weather,
        'translate_lighting': translate_lighting,
    }
    
    return render(request, 'car_detector/analysis_detail.html', context)


def analysis_list(request):
    """Список всех анализов"""
    analyses = CarAnalysis.objects.all()
    return render(request, 'car_detector/analysis_list.html', {
        'analyses': analyses
    })


@csrf_exempt
@require_http_methods(["POST"])
def api_analyze(request):
    """API endpoint для анализа изображения"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Сохраняем во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        # Анализируем
        analysis_results = car_analysis_service.analyze_image(temp_path)
        
        # Удаляем временный файл
        os.unlink(temp_path)
        
        return JsonResponse({
            'success': True,
            'results': analysis_results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_gemini_analyze(request):
    """API endpoint для анализа изображения только с помощью Gemini"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Проверяем тип файла по расширению
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = os.path.splitext(image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return JsonResponse({'error': f'File must be an image. Got extension: {file_extension}'}, status=400)
        
        # Сохраняем изображение во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        # Анализируем изображение только с помощью Gemini
        try:
            import time
            start_time = time.time()
            
            gemini_results = car_analysis_service.gemini_analyzer.analyze(temp_path)
            processing_time = time.time() - start_time
            
            # Форматируем ответ
            response_data = {
                'status': 'success',
                'model': 'gemini',
                'results': gemini_results,
                'processing_time': round(processing_time, 2)
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': f'Gemini analysis failed: {str(e)}'
            }, status=500)
        
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def api_simple_status(request):
    """API endpoint для получения простого статуса автомобиля"""
    try:
        if 'image' not in request.FILES:
            return JsonResponse({'error': 'No image provided'}, status=400)
        
        image_file = request.FILES['image']
        
        # Проверяем тип файла по расширению
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        file_extension = os.path.splitext(image_file.name)[1].lower()
        if file_extension not in allowed_extensions:
            return JsonResponse({'error': f'File must be an image. Got extension: {file_extension}'}, status=400)
        
        # Сохраняем изображение во временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            for chunk in image_file.chunks():
                temp_file.write(chunk)
            temp_path = temp_file.name
        
        # Анализируем изображение только с помощью Gemini
        try:
            import time
            start_time = time.time()
            
            gemini_results = car_analysis_service.gemini_analyzer.analyze(temp_path)
            processing_time = time.time() - start_time
            
            # Формируем простой ответ
            integrity = gemini_results.get('integrity', {})
            cleanliness = gemini_results.get('cleanliness', {})
            damage_details = gemini_results.get('damage_details', {})
            
            # Определяем общий статус
            if integrity.get('label') == 'damaged':
                status = "damaged"
                status_text = "Автомобиль поврежден"
            else:
                status = "good"
                status_text = "Автомобиль в хорошем состоянии"
            
            # Считаем количество повреждений
            damage_count = len(damage_details.get('parts', []))
            
            # Определяем уровень чистоты
            cleanliness_level = cleanliness.get('label', 'unknown')
            if cleanliness_level == 'clean':
                cleanliness_text = "чистый"
            elif cleanliness_level == 'slightly_dirty':
                cleanliness_text = "слегка грязный"
            else:
                cleanliness_text = "грязный"
            
            # Формируем простой ответ
            response_data = {
                'status': 'success',
                'car_status': status,
                'car_status_text': status_text,
                'damage_count': damage_count,
                'cleanliness': cleanliness_text,
                'confidence': round(integrity.get('confidence', 0) * 100, 1),
                'processing_time': round(processing_time, 2)
            }
            
            return JsonResponse(response_data)
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'error': f'Analysis failed: {str(e)}'
            }, status=500)
        
        finally:
            # Удаляем временный файл
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'error': str(e)
        }, status=500)
