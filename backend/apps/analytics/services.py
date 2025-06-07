# ============ apps/analytics/services.py ============
from django.db.models import Count, Avg, F
from django.utils import timezone
from datetime import timedelta, date
from .models import UserActivity, ApplicationMetrics, SystemMetrics
from apps.legal_forms.models import LegalApplication
import logging

logger = logging.getLogger(__name__)

class AnalyticsService:
    def track_user_activity(self, user, activity_type, resource_id=None, metadata=None, request=None):
        """Track user activity"""
        try:
            activity_data = {
                'user': user,
                'activity_type': activity_type,
                'resource_id': resource_id or '',
                'metadata': metadata or {},
            }
            
            if request:
                activity_data['ip_address'] = self._get_client_ip(request)
                activity_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            UserActivity.objects.create(**activity_data)
            
        except Exception as e:
            logger.error(f"Failed to track user activity: {e}")

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def generate_daily_metrics(self, target_date=None):
        """Generate daily system metrics"""
        if not target_date:
            target_date = date.today() - timedelta(days=1)
        
        try:
            # Applications created today
            apps_created = LegalApplication.objects.filter(
                created_at__date=target_date
            ).count()
            
            # Applications submitted today
            apps_submitted = LegalApplication.objects.filter(
                submitted_at__date=target_date
            ).count()
            
            # Active users today
            active_users = UserActivity.objects.filter(
                timestamp__date=target_date
            ).values('user').distinct().count()
            
            # Speech recognition usage
            speech_usage = UserActivity.objects.filter(
                timestamp__date=target_date,
                activity_type='speech_recognition'
            ).count()
            
            # Average completion time
            avg_completion_time = ApplicationMetrics.objects.filter(
                created_at__date=target_date,
                time_to_complete__isnull=False
            ).aggregate(avg_time=Avg('time_to_complete'))['avg_time']
            
            # Store metrics
            metrics = [
                ('applications_created', apps_created),
                ('applications_submitted', apps_submitted),
                ('active_users', active_users),
                ('speech_usage_count', speech_usage),
                ('avg_completion_time_seconds', 
                 avg_completion_time.total_seconds() if avg_completion_time else 0),
            ]
            
            for metric_name, metric_value in metrics:
                SystemMetrics.objects.update_or_create(
                    metric_name=metric_name,
                    metric_date=target_date,
                    defaults={'metric_value': metric_value}
                )
                
            logger.info(f"Generated daily metrics for {target_date}")
            
        except Exception as e:
            logger.error(f"Failed to generate daily metrics: {e}")

    def get_user_analytics(self, user, days=30):
        """Get analytics for a specific user"""
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        activities = UserActivity.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        return {
            'total_activities': activities.count(),
            'activity_breakdown': activities.values('activity_type').annotate(
                count=Count('id')
            ),
            'applications_created': activities.filter(
                activity_type='application_create'
            ).count(),
            'speech_usage': activities.filter(
                activity_type='speech_recognition'
            ).count(),
            'last_login': activities.filter(
                activity_type='login'
            ).first(),
        }