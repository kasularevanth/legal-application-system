# ============ apps/notifications/services.py ============
from django.core.mail import send_mail
from django.conf import settings
from django.template import Template, Context
from .models import Notification, NotificationTemplate, UserPreferences
import logging
import requests

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.sms_api_key = getattr(settings, 'SMS_API_KEY', None)
        self.sms_api_url = getattr(settings, 'SMS_API_URL', None)

    def send_notification(self, user, notification_type, template_name, context_data):
        """Send notification based on type and template"""
        try:
            # Get user preferences
            preferences, _ = UserPreferences.objects.get_or_create(user=user)
            
            # Check if user wants this type of notification
            if not self._check_user_preference(preferences, notification_type):
                return False

            # Get template
            template = NotificationTemplate.objects.get(
                name=template_name,
                is_active=True
            )

            # Render template content
            subject = Template(template.subject_template).render(Context(context_data))
            message = Template(template.body_template).render(Context(context_data))

            # Create notification record
            notification = Notification.objects.create(
                user=user,
                application=context_data.get('application'),
                notification_type=notification_type,
                subject=subject,
                message=message,
                status='pending'
            )

            # Send based on type
            if notification_type == 'email':
                success = self._send_email(user.email, subject, message)
            elif notification_type == 'sms':
                sms_message = Template(template.sms_template).render(Context(context_data))
                success = self._send_sms(user.phone_number, sms_message)
            else:
                success = True  # For in-app notifications

            # Update notification status
            notification.status = 'sent' if success else 'failed'
            if success:
                notification.sent_at = timezone.now()
            notification.save()

            return success

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    def _send_email(self, to_email, subject, message):
        """Send email notification"""
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[to_email],
                html_message=message,
                fail_silently=False
            )
            return True
        except Exception as e:
            logger.error(f"Email sending failed: {e}")
            return False

    def _send_sms(self, phone_number, message):
        """Send SMS notification"""
        if not self.sms_api_key or not phone_number:
            return False
            
        try:
            response = requests.post(
                self.sms_api_url,
                json={
                    'api_key': self.sms_api_key,
                    'to': phone_number,
                    'message': message
                },
                timeout=30
            )
            return response.status_code == 200
        except Exception as e:
            logger.error(f"SMS sending failed: {e}")
            return False

    def _check_user_preference(self, preferences, notification_type):
        """Check if user has enabled this notification type"""
        if notification_type == 'email':
            return preferences.email_notifications
        elif notification_type == 'sms':
            return preferences.sms_notifications
        elif notification_type == 'push':
            return preferences.push_notifications
        return True

    def send_application_status_update(self, application):
        """Send notification when application status changes"""
        context = {
            'application': application,
            'user': application.user,
            'status': application.status,
            'application_id': application.application_id,
            'title': application.title,
        }

        # Send email notification
        self.send_notification(
            user=application.user,
            notification_type='email',
            template_name='application_status_update',
            context_data=context
        )

        # Send SMS for important status changes
        if application.status in ['approved', 'rejected']:
            self.send_notification(
                user=application.user,
                notification_type='sms',
                template_name='application_status_update',
                context_data=context
            )