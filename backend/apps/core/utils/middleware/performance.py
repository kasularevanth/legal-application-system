

# ============ backend/apps/core/middleware/performance.py ============
import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger('performance')

class PerformanceMiddleware(MiddlewareMixin):
    """Middleware to track API performance"""
    
    def process_request(self, request):
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests
            if duration > 2.0:  # Log requests taking more than 2 seconds
                logger.warning(
                    f"Slow request: {request.method} {request.path} "
                    f"took {duration:.2f}s (Status: {response.status_code})"
                )
            
            # Store metrics for API endpoints
            if request.path.startswith('/api/'):
                metric_key = f"api_metrics_{request.path}_{int(time.time())}"
                cache.set(
                    metric_key,
                    {
                        'method': request.method,
                        'path': request.path,
                        'duration': duration,
                        'status_code': response.status_code,
                        'user_id': getattr(request.user, 'id', None) if hasattr(request, 'user') else None
                    },
                    timeout=3600  # Keep for 1 hour
                )
        
        return response