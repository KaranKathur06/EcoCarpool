import time
import logging
from functools import wraps
from django.db import connection
from django.conf import settings
from django.core.cache import cache
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class PerformanceMonitor:
    """Monitor and track application performance metrics"""
    
    def __init__(self):
        self.metrics = {}
        self.query_counts = {}
        self.slow_queries = []
    
    def track_execution_time(self, func_name: str, execution_time: float):
        """Track function execution time"""
        if func_name not in self.metrics:
            self.metrics[func_name] = {
                'total_time': 0,
                'call_count': 0,
                'avg_time': 0,
                'max_time': 0,
                'min_time': float('inf')
            }
        
        metric = self.metrics[func_name]
        metric['total_time'] += execution_time
        metric['call_count'] += 1
        metric['avg_time'] = metric['total_time'] / metric['call_count']
        metric['max_time'] = max(metric['max_time'], execution_time)
        metric['min_time'] = min(metric['min_time'], execution_time)
    
    def track_query_count(self, func_name: str, query_count: int):
        """Track database query count for function"""
        if func_name not in self.query_counts:
            self.query_counts[func_name] = {
                'total_queries': 0,
                'call_count': 0,
                'avg_queries': 0,
                'max_queries': 0
            }
        
        metric = self.query_counts[func_name]
        metric['total_queries'] += query_count
        metric['call_count'] += 1
        metric['avg_queries'] = metric['total_queries'] / metric['call_count']
        metric['max_queries'] = max(metric['max_queries'], query_count)
    
    def log_slow_query(self, query: str, execution_time: float):
        """Log slow database queries"""
        if execution_time > 1.0:  # Queries slower than 1 second
            self.slow_queries.append({
                'query': query,
                'execution_time': execution_time,
                'timestamp': time.time()
            })
            logger.warning(f"Slow query detected: {execution_time:.2f}s - {query[:100]}...")
    
    def get_performance_report(self) -> Dict:
        """Generate performance report"""
        return {
            'execution_metrics': self.metrics,
            'query_metrics': self.query_counts,
            'slow_queries': self.slow_queries[-10:],  # Last 10 slow queries
            'total_functions_monitored': len(self.metrics),
            'total_slow_queries': len(self.slow_queries)
        }

# Global performance monitor instance
performance_monitor = PerformanceMonitor()

def monitor_performance(func):
    """Decorator to monitor function performance"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        func_name = f"{func.__module__}.{func.__name__}"
        
        # Track initial query count
        initial_queries = len(connection.queries)
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            # Calculate metrics
            end_time = time.time()
            execution_time = end_time - start_time
            query_count = len(connection.queries) - initial_queries
            
            # Track metrics
            performance_monitor.track_execution_time(func_name, execution_time)
            performance_monitor.track_query_count(func_name, query_count)
            
            # Log slow functions
            if execution_time > 2.0:  # Functions slower than 2 seconds
                logger.warning(
                    f"Slow function: {func_name} took {execution_time:.2f}s "
                    f"with {query_count} queries"
                )
            
            # Log queries if in debug mode
            if settings.DEBUG and query_count > 10:
                logger.info(f"High query count: {func_name} executed {query_count} queries")
    
    return wrapper

def optimize_queryset(queryset, select_related=None, prefetch_related=None):
    """Optimize queryset with select_related and prefetch_related"""
    if select_related:
        queryset = queryset.select_related(*select_related)
    
    if prefetch_related:
        queryset = queryset.prefetch_related(*prefetch_related)
    
    return queryset

class DatabaseOptimizer:
    """Database query optimization utilities"""
    
    @staticmethod
    def get_optimized_rides_queryset():
        """Get optimized rides queryset with related data"""
        from rides.models import Ride
        
        return Ride.objects.select_related(
            'driver',
            'vehicle',
            'vehicle__company',
            'vehicle__model'
        ).prefetch_related(
            'bookings',
            'bookings__passenger',
            'reviews'
        )
    
    @staticmethod
    def get_optimized_bookings_queryset():
        """Get optimized bookings queryset with related data"""
        from rides.models import Booking
        
        return Booking.objects.select_related(
            'ride',
            'ride__driver',
            'ride__vehicle',
            'passenger'
        ).prefetch_related(
            'payments',
            'reviews'
        )
    
    @staticmethod
    def get_optimized_users_queryset():
        """Get optimized users queryset with related data"""
        from users.models import CustomUser
        
        return CustomUser.objects.prefetch_related(
            'vehicles',
            'driver_rides',
            'bookings',
            'reviews_given',
            'reviews_received'
        )

class CacheWarmer:
    """Warm up frequently accessed cache entries"""
    
    @staticmethod
    def warm_popular_routes():
        """Pre-cache popular routes"""
        from utils.cache import RideSearchCache
        RideSearchCache.get_popular_routes()
        logger.info("Warmed up popular routes cache")
    
    @staticmethod
    def warm_user_stats(user_ids: List[int]):
        """Pre-cache user statistics for given users"""
        from utils.cache import UserStatsCache
        
        for user_id in user_ids:
            UserStatsCache.get_user_stats(user_id)
        
        logger.info(f"Warmed up user stats cache for {len(user_ids)} users")
    
    @staticmethod
    def warm_dashboard_stats(user_ids: List[int]):
        """Pre-cache dashboard statistics for active users"""
        from utils.cache import DashboardCache
        
        for user_id in user_ids:
            DashboardCache.get_dashboard_stats(user_id)
        
        logger.info(f"Warmed up dashboard stats cache for {len(user_ids)} users")

def batch_process(queryset, batch_size=1000, callback=None):
    """Process queryset in batches to avoid memory issues"""
    total_processed = 0
    
    while True:
        batch = list(queryset[total_processed:total_processed + batch_size])
        if not batch:
            break
        
        if callback:
            callback(batch)
        
        total_processed += len(batch)
        
        if len(batch) < batch_size:
            break
    
    return total_processed

class QueryAnalyzer:
    """Analyze and optimize database queries"""
    
    @staticmethod
    def analyze_slow_queries():
        """Analyze slow queries and provide optimization suggestions"""
        slow_queries = performance_monitor.slow_queries
        
        suggestions = []
        for query_info in slow_queries:
            query = query_info['query']
            
            # Basic analysis
            if 'JOIN' not in query.upper() and 'SELECT' in query.upper():
                suggestions.append({
                    'query': query[:100],
                    'suggestion': 'Consider using select_related() for foreign key relationships'
                })
            
            if 'IN (' in query.upper():
                suggestions.append({
                    'query': query[:100],
                    'suggestion': 'Consider using prefetch_related() for reverse foreign key lookups'
                })
        
        return suggestions
    
    @staticmethod
    def get_query_statistics():
        """Get database query statistics"""
        return {
            'total_queries': len(connection.queries),
            'query_metrics': performance_monitor.query_counts,
            'slow_queries_count': len(performance_monitor.slow_queries),
            'optimization_suggestions': QueryAnalyzer.analyze_slow_queries()
        }

# Middleware to track request performance
class PerformanceMiddleware:
    """Middleware to track request performance"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        start_time = time.time()
        initial_queries = len(connection.queries)
        
        response = self.get_response(request)
        
        # Calculate metrics
        end_time = time.time()
        execution_time = end_time - start_time
        query_count = len(connection.queries) - initial_queries
        
        # Add performance headers
        response['X-Response-Time'] = f"{execution_time:.3f}s"
        response['X-Query-Count'] = str(query_count)
        
        # Log slow requests
        if execution_time > 3.0:  # Requests slower than 3 seconds
            logger.warning(
                f"Slow request: {request.path} took {execution_time:.2f}s "
                f"with {query_count} queries"
            )
        
        return response
