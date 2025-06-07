
# ============ apps/document_processing/urls.py ============
from django.urls import path
from . import views

urlpatterns = [
    path('download/<int:application_id>/', views.download_application_pdf, name='download_application'),
    path('download-all/', views.download_all_applications, name='download_all_applications'),
    path('analyze/<int:application_id>/', views.analyze_document, name='analyze_document'),
]