
# ============ legal_app_backend/settings.py ============
import os
from decouple import config
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-key')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1').split(',')

# Custom user model
AUTH_USER_MODEL = 'authentication.User'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'apps.authentication.apps.AuthenticationConfig',
    'apps.legal_forms.apps.LegalFormsConfig',
    'apps.speech_processing.apps.SpeechProcessingConfig',
    'apps.document_processing.apps.DocumentProcessingConfig',
    'apps.notifications.apps.NotificationsConfig',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.JWTAuthenticationMiddleware',
]

ROOT_URLCONF = 'legal_app_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'legal_app_db',
        'USER': 'postgres',
        'PASSWORD': '',  # No password by default for local development
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# BHASHINI API Configuration
BHASHINI_API_KEY = config('BHASHINI_API_KEY', default='34e48c4340-e39e-4585-b196-ec1ccb3')
BHASHINI_USER_ID = config('BHASHINI_USER_ID', default='udyat')
BHASHINI_INFERENCE_API_KEY = config('BHASHINI_INFERENCE_API_KEY', 
    default='uPUvNS1__NtJYtMIyyu6QGMFLzZWccanxPanZE7QR4vO2Ljumu8T87tX69MPdy7fuPUvNS1__NtJYtMI4vO2Ljumu8T87tX69MPdy7f')
BHASHINI_BASE_URL = config('BHASHINI_BASE_URL', default='https://meity-auth.ulcacontrib.org')

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = config('AZURE_OPENAI_ENDPOINT')
AZURE_OPENAI_API_KEY = config('AZURE_OPENAI_API_KEY')
AZURE_OPENAI_API_VERSION = config('AZURE_OPENAI_API_VERSION', default='2023-12-01-preview')
AZURE_OPENAI_DEPLOYMENT_NAME = config('AZURE_OPENAI_DEPLOYMENT_NAME', default='gpt-4')

# Azure Storage Configuration
AZURE_ACCOUNT_NAME = config('AZURE_ACCOUNT_NAME')
AZURE_ACCOUNT_KEY = config('AZURE_ACCOUNT_KEY')
AZURE_CONTAINER = config('AZURE_CONTAINER', default='legal-documents')

# Media and Static Files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Celery Configuration
CELERY_BROKER_URL = config('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = config('REDIS_URL', default='redis://localhost:6379/0')

# CORS Configuration
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = DEBUG

# JWT Configuration
JWT_SECRET_KEY = config('JWT_SECRET_KEY', default=SECRET_KEY)
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = 86400  # 24 hours

# Language Configuration
LANGUAGE_CODE = 'en-us'
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'hi': 'हिंदी',
    'te': 'తెలుగు',
    'ta': 'தமிழ்',
    'bn': 'বাংলা',
    'gu': 'ગુજરાતી',
    'kn': 'ಕನ್ನಡ',
    'ml': 'മലയാളം',
    'mr': 'मराठी',
    'or': 'ଓଡ଼ିଆ',
    'pa': 'ਪੰਜਾਬੀ',
    'ur': 'اردو',
}
