from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dual-analysis/', views.dual_analysis, name='dual_analysis'),
    path('upload/', views.upload_and_analyze, name='upload_and_analyze'),
    path('analysis/<int:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    path('analyses/', views.analysis_list, name='analysis_list'),
    path('api/analyze/', views.api_analyze, name='api_analyze'),
    path('api/gemini-analyze/', views.api_gemini_analyze, name='api_gemini_analyze'),
    path('api/simple-status/', views.api_simple_status, name='api_simple_status'),
]
