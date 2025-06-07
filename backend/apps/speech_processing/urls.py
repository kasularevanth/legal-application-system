# ============ apps/speech_processing/urls.py ============
from django.urls import path
from . import views

urlpatterns = [
    path('speech-to-text/', views.speech_to_text, name='speech_to_text'),
    path('text-to-speech/', views.text_to_speech, name='text_to_speech'),
    path('analyze-speech/', views.analyze_speech_for_form, name='analyze_speech_for_form'),
    path('translate/', views.translate_text, name='translate_text'),
]
