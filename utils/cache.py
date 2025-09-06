from django.core.cache import cache
from django.conf import settings
from functools import wraps
import hashlib
import json
from typing import Any, Optional

class CacheManager:
    """Centralized cache management for the EcoCarpool application"""
    
    # Cache timeouts (in seconds)
    TIMEOUTS = {
        'user_stats': 3600,  # 1 hour
        'ride_search': 300,  # 5 minutes
        'vehicle_list': 1800,  # 30 minutes
        'dashboard_stats': 600,  # 10 minutes
        'reviews': 1800,  # 30 minutes
        'popular_routes': 7200,  # 2 hours
    }
    
    @staticmethod
    def generate_key(*args, **kwargs) -> str:
        """Generate a cache key from arguments"""
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_string = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get value from cache"""
        return cache.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any, timeout: Optional[int] = None) -> None:
        """Set value in cache"""
        cache.set(key, value, timeout)
    
    @classmethod
    def delete(cls, key: str) -> None:
        """Delete key from cache"""
        cache.delete(key)
    
    @classmethod
    def clear_pattern(cls, pattern: str) -> None:
        """Clear all keys matching pattern"""
        if hasattr(cache, 'delete_pattern'):
            cache.delete_pattern(pattern)
    
    @classmethod
    def get_user_stats_key(cls, user_id: int) -> str:
        """Get cache key for user statistics"""
        return f"user_stats_{user_id}"
    
    @classmethod
    def get_ride_search_key(cls, **filters) -> str:
        """Get cache key for ride search results"""
        key = cls.generate_key(**filters)
        return f"ride_search_{key}"
    
    @classmethod
    def get_dashboard_stats_key(cls, user_id: int) -> str:
        """Get cache key for dashboard statistics"""
        return f"dashboard_stats_{user_id}"
    
    @classmethod
    def invalidate_user_cache(cls, user_id: int) -> None:
        """Invalidate all cache entries for a user"""
        keys_to_delete = [
            cls.get_user_stats_key(user_id),
            cls.get_dashboard_stats_key(user_id),
        ]
        for key in keys_to_delete:
            cls.delete(key)


def cache_result(timeout: int = 300, key_prefix: str = ''):
    """Decorator to cache function results"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            key_data = {
                'func': f"{func.__module__}.{func.__name__}",
                'args': args,
                'kwargs': kwargs
            }
            cache_key = f"{key_prefix}_{CacheManager.generate_key(**key_data)}"
            
            # Try to get from cache
            result = CacheManager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            CacheManager.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def invalidate_cache_on_save(cache_keys: list):
    """Decorator to invalidate cache when model is saved"""
    def decorator(model_class):
        original_save = model_class.save
        
        def save_with_cache_invalidation(self, *args, **kwargs):
            result = original_save(self, *args, **kwargs)
            
            # Invalidate specified cache keys
            for key_template in cache_keys:
                if hasattr(self, 'id'):
                    key = key_template.format(id=self.id)
                    CacheManager.delete(key)
            
            return result
        
        model_class.save = save_with_cache_invalidation
        return model_class
    return decorator


class RideSearchCache:
    """Specialized caching for ride search functionality"""
    
    @staticmethod
    def get_popular_routes(limit: int = 10):
        """Get cached popular routes"""
        cache_key = f"popular_routes_{limit}"
        routes = CacheManager.get(cache_key)
        
        if routes is None:
            from rides.models import Ride
            from django.db.models import Count
            
            routes = Ride.objects.values(
                'start_location', 'end_location'
            ).annotate(
                ride_count=Count('id')
            ).order_by('-ride_count')[:limit]
            
            CacheManager.set(
                cache_key, 
                list(routes), 
                CacheManager.TIMEOUTS['popular_routes']
            )
        
        return routes
    
    @staticmethod
    def get_ride_recommendations(user_id: int, limit: int = 5):
        """Get cached ride recommendations for user"""
        cache_key = f"ride_recommendations_{user_id}_{limit}"
        recommendations = CacheManager.get(cache_key)
        
        if recommendations is None:
            from rides.models import Ride, Booking
            from django.db.models import Q
            
            # Get user's booking history to find preferred routes
            user_bookings = Booking.objects.filter(
                passenger_id=user_id,
                status='completed'
            ).values_list('ride__start_location', 'ride__end_location')
            
            # Find similar routes
            route_conditions = Q()
            for start, end in user_bookings:
                route_conditions |= Q(start_location=start) | Q(end_location=end)
            
            recommendations = Ride.objects.filter(
                route_conditions,
                status='active'
            ).exclude(
                driver_id=user_id
            ).order_by('-created_at')[:limit]
            
            CacheManager.set(
                cache_key,
                list(recommendations.values()),
                CacheManager.TIMEOUTS['ride_search']
            )
        
        return recommendations


class UserStatsCache:
    """Specialized caching for user statistics"""
    
    @staticmethod
    def get_user_stats(user_id: int):
        """Get cached user statistics"""
        cache_key = CacheManager.get_user_stats_key(user_id)
        stats = CacheManager.get(cache_key)
        
        if stats is None:
            from users.models import CustomUser
            from django.db.models import Sum, Avg, Count
            
            try:
                user = CustomUser.objects.get(id=user_id)
                
                # Calculate statistics
                driver_rides = user.driver_rides.filter(status='completed')
                passenger_bookings = user.bookings.filter(status='completed')
                
                stats = {
                    'total_rides_as_driver': driver_rides.count(),
                    'total_rides_as_passenger': passenger_bookings.count(),
                    'total_earnings': user.get_total_earnings(),
                    'average_rating': user.get_average_rating(),
                    'co2_saved': user.get_co2_saved(),
                    'fuel_saved': user.get_fuel_saved(),
                }
                
                CacheManager.set(
                    cache_key,
                    stats,
                    CacheManager.TIMEOUTS['user_stats']
                )
            except CustomUser.DoesNotExist:
                stats = {}
        
        return stats
    
    @staticmethod
    def invalidate_user_stats(user_id: int):
        """Invalidate user statistics cache"""
        cache_key = CacheManager.get_user_stats_key(user_id)
        CacheManager.delete(cache_key)


class DashboardCache:
    """Specialized caching for dashboard data"""
    
    @staticmethod
    def get_dashboard_stats(user_id: int):
        """Get cached dashboard statistics"""
        cache_key = CacheManager.get_dashboard_stats_key(user_id)
        stats = CacheManager.get(cache_key)
        
        if stats is None:
            from rides.models import Ride, Booking
            from payments.models import Payment
            from django.utils import timezone
            from datetime import timedelta
            
            # Calculate dashboard statistics
            today = timezone.now().date()
            this_month = today.replace(day=1)
            
            # Rides statistics
            total_rides = Ride.objects.filter(driver_id=user_id).count()
            active_rides = Ride.objects.filter(
                driver_id=user_id,
                status='active'
            ).count()
            
            # Bookings statistics
            total_bookings = Booking.objects.filter(passenger_id=user_id).count()
            upcoming_bookings = Booking.objects.filter(
                passenger_id=user_id,
                status='confirmed',
                ride__ride_date__gte=timezone.now()
            ).count()
            
            # Earnings this month
            monthly_earnings = Payment.objects.filter(
                receiver_id=user_id,
                status='completed',
                created_at__gte=this_month
            ).aggregate(
                total=Sum('net_amount')
            )['total'] or 0
            
            stats = {
                'total_rides': total_rides,
                'active_rides': active_rides,
                'total_bookings': total_bookings,
                'upcoming_bookings': upcoming_bookings,
                'monthly_earnings': float(monthly_earnings),
                'last_updated': timezone.now().isoformat(),
            }
            
            CacheManager.set(
                cache_key,
                stats,
                CacheManager.TIMEOUTS['dashboard_stats']
            )
        
        return stats
