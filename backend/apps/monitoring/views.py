# ============ apps/monitoring/views.py ============
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache
from django.db import connection
from django.core.cache import cache
import redis
import os
import psutil
from datetime import datetime

@require_GET
@never_cache
def health_check(request):
    """Comprehensive health check endpoint"""
    health_status = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = {'status': 'healthy'}
    except Exception as e:
        health_status['checks']['database'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'unhealthy'
    
    # Redis check
    try:
        cache.set('health_check', 'ok', 10)
        result = cache.get('health_check')
        if result == 'ok':
            health_status['checks']['redis'] = {'status': 'healthy'}
        else:
            raise Exception("Cache test failed")
    except Exception as e:
        health_status['checks']['redis'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'unhealthy'
    
    # System resources check
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        health_status['checks']['system'] = {
            'status': 'healthy',
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'disk_percent': disk.percent
        }
        
        # Alert if resources are high
        if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
            health_status['checks']['system']['status'] = 'warning'
            
    except Exception as e:
        health_status['checks']['system'] = {'status': 'unhealthy', 'error': str(e)}
    
    # Application-specific checks
    try:
        from apps.legal_forms.models import FormTemplate
        template_count = FormTemplate.objects.filter(is_active=True).count()
        health_status['checks']['application'] = {
            'status': 'healthy',
            'active_templates': template_count
        }
    except Exception as e:
        health_status['checks']['application'] = {'status': 'unhealthy', 'error': str(e)}
        health_status['status'] = 'unhealthy'
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return JsonResponse(health_status, status=status_code)

@require_GET
def metrics(request):
    """Prometheus-style metrics endpoint"""
    try:
        from apps.legal_forms.models import LegalApplication
        from apps.authentication.models import User
        
        # Application metrics
        total_applications = LegalApplication.objects.count()
        submitted_applications = LegalApplication.objects.filter(status='submitted').count()
        total_users = User.objects.count()
        active_users_today = User.objects.filter(last_login__date=datetime.now().date()).count()
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        metrics_data = {
            'legal_applications_total': total_applications,
            'legal_applications_submitted': submitted_applications,
            'users_total': total_users,
            'users_active_today': active_users_today,
            'system_cpu_percent': cpu_percent,
            'system_memory_percent': memory.percent,
        }
        
        return JsonResponse(metrics_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)