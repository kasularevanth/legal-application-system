# apps/legal_forms/urls.py (Updated)
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import legal_case_views

router = DefaultRouter()
router.register(r'templates', views.FormTemplateViewSet)
router.register(r'applications', views.LegalApplicationViewSet, basename='application')
router.register(r'knowledge-base', views.LegalKnowledgeBaseViewSet)

urlpatterns = [
    # Existing routes
    path('', include(router.urls)),
    
    # Legal case processing routes
    path('legal-case/process-input/', legal_case_views.process_initial_input, name='process_initial_input'),
    path('legal-case/submit-answer/', legal_case_views.submit_answer, name='submit_answer'),
    path('legal-case/generate-document/', legal_case_views.generate_document, name='generate_document'),
    path('legal-case/preview-document/', legal_case_views.preview_document, name='preview_document'),
    path('legal-case/status/<uuid:case_id>/', legal_case_views.get_case_status, name='get_case_status'),
    path('legal-case/download/<uuid:document_id>/', legal_case_views.download_document, name='download_document'),
    path('legal-case/history/', legal_case_views.get_case_history, name='get_case_history'),
    
    # Configuration endpoints
    path('legal-case/case-type-mappings/', legal_case_views.get_case_type_mappings, name='get_case_type_mappings'),
    path('legal-case/question-mappings/<str:case_type>/', legal_case_views.get_question_mappings, name='get_question_mappings'),
]