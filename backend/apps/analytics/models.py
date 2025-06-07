# ============ apps/analytics/models.py ============
from django.db import models
from apps.authentication.models import User
from apps.legal_forms.models import LegalApplication, FormTemplate

class UserActivity(models.Model):
    """Track user activities for analytics"""
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('form_view', 'Form Template Viewed'),
        ('application_create', 'Application Created'),
        ('application_submit', 'Application Submitted'),
        ('speech_recognition', 'Speech Recognition Used'),
        ('document_download', 'Document Downloaded'),
        ('help_accessed', 'Help/Knowledge Base Accessed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    resource_id = models.CharField(max_length=100, blank=True)  # ID of resource accessed
    metadata = models.JSONField(default=dict)  # Additional data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['timestamp']),
        ]

class ApplicationMetrics(models.Model):
    """Track application completion metrics"""
    application = models.OneToOneField(LegalApplication, on_delete=models.CASCADE)
    time_to_complete = models.DurationField(null=True)  # Time from creation to submission
    speech_usage_count = models.PositiveIntegerField(default=0)
    form_saves_count = models.PositiveIntegerField(default=0)
    help_accesses_count = models.PositiveIntegerField(default=0)
    completion_score = models.FloatField(null=True)  # Based on AI analysis
    created_at = models.DateTimeField(auto_now_add=True)

class SystemMetrics(models.Model):
    """System-wide metrics"""
    metric_name = models.CharField(max_length=100)
    metric_value = models.FloatField()
    metric_date = models.DateField()
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['metric_name', 'metric_date']