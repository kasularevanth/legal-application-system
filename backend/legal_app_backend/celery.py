

# ============ backend/legal_app_backend/celery.py ============
import os
from celery import Celery
from django.conf import settings

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'legal_app_backend.settings')

app = Celery('legal_app_backend')

# Configure Celery using Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks from all registered Django apps
app.autodiscover_tasks()

# Periodic tasks configuration
from celery.schedules import crontab

app.conf.beat_schedule = {
    'generate-daily-analytics': {
        'task': 'apps.tasks.generate_daily_analytics',
        'schedule': crontab(hour=1, minute=0),  # Run daily at 1 AM
    },
    'process-pending-applications': {
        'task': 'apps.tasks.process_pending_applications',
        'schedule': crontab(hour=9, minute=0),  # Run daily at 9 AM
    },
    'cleanup-old-files': {
        'task': 'apps.tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}

app.conf.timezone = 'UTC'
