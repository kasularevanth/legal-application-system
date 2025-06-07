# ============ apps/tasks.py ============
from celery import shared_task
from django.utils import timezone
from apps.notifications.services import NotificationService
from apps.analytics.services import AnalyticsService
from apps.legal_forms.models import LegalApplication
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_notification_task(user_id, notification_type, template_name, context_data):
    """Async task to send notifications"""
    try:
        from apps.authentication.models import User
        user = User.objects.get(id=user_id)
        
        notification_service = NotificationService()
        result = notification_service.send_notification(
            user=user,
            notification_type=notification_type,
            template_name=template_name,
            context_data=context_data
        )
        
        logger.info(f"Notification sent to user {user_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")
        return False

@shared_task
def generate_daily_analytics():
    """Generate daily analytics reports"""
    try:
        analytics_service = AnalyticsService()
        analytics_service.generate_daily_metrics()
        logger.info("Daily analytics generated successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to generate daily analytics: {e}")
        return False

@shared_task
def process_pending_applications():
    """Process applications that need status updates"""
    try:
        # Find applications that have been under review for more than 7 days
        cutoff_date = timezone.now() - timezone.timedelta(days=7)
        stale_applications = LegalApplication.objects.filter(
            status='under_review',
            submitted_at__lt=cutoff_date
        )
        
        notification_service = NotificationService()
        
        for application in stale_applications:
            # Send reminder notification
            context = {
                'application': application,
                'user': application.user,
                'days_pending': (timezone.now() - application.submitted_at).days
            }
            
            notification_service.send_notification(
                user=application.user,
                notification_type='email',
                template_name='application_reminder',
                context_data=context
            )
            
        logger.info(f"Processed {stale_applications.count()} pending applications")
        return stale_applications.count()
        
    except Exception as e:
        logger.error(f"Failed to process pending applications: {e}")
        return 0

@shared_task
def cleanup_old_files():
    """Clean up old temporary files"""
    import os
    from django.conf import settings
    
    try:
        # Clean up temporary audio files older than 24 hours
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        if os.path.exists(temp_dir):
            cutoff_time = timezone.now() - timezone.timedelta(hours=24)
            
            for filename in os.listdir(temp_dir):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    file_time = timezone.datetime.fromtimestamp(
                        os.path.getctime(file_path)
                    ).replace(tzinfo=timezone.get_current_timezone())
                    
                    if file_time < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"Removed old temp file: {filename}")
        
        return True
    except Exception as e:
        logger.error(f"Failed to cleanup old files: {e}")
        return False