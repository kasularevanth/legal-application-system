# ============ apps/security/middleware.py ============
import logging
import time
from django.http import HttpResponseForbidden
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import json

logger = logging.getLogger('django.security')

class SecurityMiddleware(MiddlewareMixin):
    """Advanced security middleware for the application"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_requests_per_minute = getattr(settings, 'RATE_LIMIT_REQUESTS', 60)
        self.blocked_ips = set()
        
    def process_request(self, request):
        # Rate limiting
        if self._is_rate_limited(request):
            logger.warning(f"Rate limit exceeded for IP: {self._get_client_ip(request)}")
            return HttpResponseForbidden("Rate limit exceeded")
        
        # IP blocking
        client_ip = self._get_client_ip(request)
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            return HttpResponseForbidden("Access denied")
        
        # Log suspicious activities
        self._log_suspicious_activity(request)
        
        return None

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _is_rate_limited(self, request):
        client_ip = self._get_client_ip(request)
        cache_key = f"rate_limit_{client_ip}"
        
        current_requests = cache.get(cache_key, 0)
        if current_requests >= self.max_requests_per_minute:
            return True
        
        cache.set(cache_key, current_requests + 1, 60)  # 1 minute timeout
        return False

    def _log_suspicious_activity(self, request):
        """Log potentially suspicious activities"""
        suspicious_patterns = [
            'admin', 'wp-admin', 'phpmyadmin', '.env', 'config',
            'backup', 'dump', 'sql', 'shell', 'cmd'
        ]
        
        path = request.path.lower()
        if any(pattern in path for pattern in suspicious_patterns):
            logger.warning(f"Suspicious path accessed: {path} from IP: {self._get_client_ip(request)}")

class AuditLogMiddleware(MiddlewareMixin):
    """Middleware to log all API requests for audit purposes"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        request.start_time = time.time()
        return None

    def process_response(self, request, response):
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log API requests
            if request.path.startswith('/api/'):
                log_data = {
                    'method': request.method,
                    'path': request.path,
                    'status_code': response.status_code,
                    'duration': duration,
                    'ip': self._get_client_ip(request),
                    'user': str(request.user) if hasattr(request, 'user') else 'Anonymous',
                    'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
                }
                
                logger.info(f"API Request: {json.dumps(log_data)}")
        
        return response

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip