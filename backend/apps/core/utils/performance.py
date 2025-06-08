



-- ============ backend/apps/core/utils/performance.py ============
import time
import logging
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from typing import Optional, Any, Callable
import hashlib
import json

logger = logging.getLogger(__name__)

def cached_result(timeout: int = 300, key_prefix: str = ''):
    """
    Decorator to cache function results
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{_generate_cache_key(args, kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                logger.debug(f"Cache hit for {cache_key}")
                return result
            
            # Execute function and cache result
            start_time = time.time()
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            # Cache the result
            cache.set(cache_key, result, timeout)
            logger.debug(f"Cached result for {cache_key} (execution time: {execution_time:.2f}s)")
            
            return result
        
        return wrapper
    return decorator

def _generate_cache_key(args: tuple, kwargs: dict) -> str:
    """Generate a cache key from function arguments"""
    key_data = {
        'args': args,
        'kwargs': kwargs
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()

def time_function(func: Callable) -> Callable:
    """
    Decorator to time function execution
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = time.time() - start_time
        
        logger.info(f"{func.__name__} executed in {execution_time:.4f} seconds")
        
        # Store performance metrics if configured
        if getattr(settings, 'ENABLE_PERFORMANCE_TRACKING', False):
            cache.set(
                f"perf_metrics_{func.__name__}_{int(start_time)}",
                {
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'timestamp': start_time
                },
                timeout=3600  # Keep for 1 hour
            )
        
        return result
    
    return wrapper

class PerformanceTracker:
    """Track and analyze performance metrics"""
    
    @staticmethod
    def get_function_stats(function_name: str, hours: int = 24) -> dict:
        """Get performance statistics for a function"""
        # This would typically query a proper metrics store
        # For now, we'll use cache keys
        metrics = []
        cache_keys = cache.keys(f"perf_metrics_{function_name}_*")
        
        for key in cache_keys:
            metric = cache.get(key)
            if metric:
                metrics.append(metric)
        
        if not metrics:
            return {}
        
        execution_times = [m['execution_time'] for m in metrics]
        
        return {
            'function': function_name,
            'total_calls': len(metrics),
            'avg_execution_time': sum(execution_times) / len(execution_times),
            'min_execution_time': min(execution_times),
            'max_execution_time': max(execution_times),
            'recent_calls': len(metrics)
        }