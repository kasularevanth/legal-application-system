# ============ apps/monitoring/performance.py ============
import time
import logging
from functools import wraps
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('apps.monitoring')

def monitor_performance(operation_name):
    """Decorator to monitor function performance"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                success = True
                error = None
            except Exception as e:
                result = None
                success = False
                error = str(e)
                raise
            finally:
                end_time = time.time()
                duration = end_time - start_time
                
                # Log performance metrics
                log_data = {
                    'operation': operation_name,
                    'duration': duration,
                    'success': success,
                    'error': error
                }
                
                logger.info(f"Performance: {log_data}")
                
                # Store metrics in cache for monitoring
                cache_key = f"perf_metrics_{operation_name}"
                metrics = cache.get(cache_key, [])
                metrics.append({
                    'timestamp': end_time,
                    'duration': duration,
                    'success': success
                })
                
                # Keep only last 100 metrics
                if len(metrics) > 100:
                    metrics = metrics[-100:]
                
                cache.set(cache_key, metrics, 3600)  # 1 hour
            
            return result
        return wrapper
    return decorator

class PerformanceMetrics:
    """Class to collect and analyze performance metrics"""
    
    @staticmethod
    def get_operation_stats(operation_name, hours=1):
        """Get performance statistics for an operation"""
        cache_key = f"perf_metrics_{operation_name}"
        metrics = cache.get(cache_key, [])
        
        if not metrics:
            return None
        
        # Filter by time window
        cutoff_time = time.time() - (hours * 3600)
        recent_metrics = [m for m in metrics if m['timestamp'] > cutoff_time]
        
        if not recent_metrics:
            return None
        
        durations = [m['duration'] for m in recent_metrics]
        success_count = sum(1 for m in recent_metrics if m['success'])
        
        return {
            'operation': operation_name,
            'total_calls': len(recent_metrics),
            'success_rate': success_count / len(recent_metrics),
            'avg_duration': sum(durations) / len(durations),
            'min_duration': min(durations),
            'max_duration': max(durations),
            'timeframe_hours': hours
        }