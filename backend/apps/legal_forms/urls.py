
# ============ apps/legal_forms/urls.py ============
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'templates', views.FormTemplateViewSet)
router.register(r'applications', views.LegalApplicationViewSet, basename='application')
router.register(r'knowledge-base', views.LegalKnowledgeBaseViewSet)

urlpatterns = [
    path('', include(router.urls)),
]