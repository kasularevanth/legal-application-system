


# ============ backend/legal_app_backend/test_settings.py ============
from .settings import *
import tempfile
import os

# Test database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True
    
    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Test cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Test media storage
MEDIA_ROOT = tempfile.mkdtemp()

# Test static files
STATIC_ROOT = tempfile.mkdtemp()

# Disable logging during tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
        'apps': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

# Test email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Test API keys (mock values)
BHASHINI_API_KEY = 'test-bhashini-key'
BHASHINI_USER_ID = 'test-user'
BHASHINI_INFERENCE_API_KEY = 'test-inference-key'
AZURE_OPENAI_ENDPOINT = 'https://test.openai.azure.com/'
AZURE_OPENAI_API_KEY = 'test-azure-key'

# Disable real API calls during tests
USE_MOCK_APIS = True

# Test JWT settings
JWT_SECRET_KEY = 'test-jwt-secret'

# Celery settings for tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
