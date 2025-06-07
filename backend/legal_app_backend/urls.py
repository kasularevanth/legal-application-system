# ============ legal_app_backend/urls.py ============
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.authentication.urls')),
    path('api/forms/', include('apps.legal_forms.urls')),
    path('api/speech/', include('apps.speech_processing.urls')),
    path('api/documents/', include('apps.document_processing.urls')),
    path('api/notifications/', include('apps.notifications.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)