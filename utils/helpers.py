"""
Helper functions for EcoCarpool application
"""
import math
import hashlib
import secrets
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    Returns distance in kilometers
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r


def calculate_estimated_duration(distance_km, avg_speed_kmh=50):
    """
    Calculate estimated duration for a trip
    Returns duration in minutes
    """
    if distance_km <= 0:
        return 0
    
    hours = distance_km / avg_speed_kmh
    minutes = hours * 60
    
    # Add buffer time for traffic and stops
    buffer_minutes = min(distance_km * 2, 30)  # 2 min per km, max 30 min
    
    return int(minutes + buffer_minutes)


def calculate_co2_savings(distance_km, passengers_count=1):
    """
    Calculate CO2 savings from carpooling
    Returns CO2 saved in kg
    """
    # Average car emits 0.21 kg CO2 per km
    co2_per_km = 0.21
    
    # Savings = (passengers - 1) * distance * emission_factor
    # Each additional passenger saves one car trip
    savings = (passengers_count - 1) * distance_km * co2_per_km
    
    return max(0, savings)


def calculate_fuel_savings(distance_km, passengers_count=1, fuel_price_per_liter=100):
    """
    Calculate fuel cost savings from carpooling
    Returns savings in currency units
    """
    # Average fuel consumption: 8 liters per 100km
    fuel_consumption_per_km = 0.08
    
    fuel_cost = distance_km * fuel_consumption_per_km * fuel_price_per_liter
    savings = (passengers_count - 1) * fuel_cost
    
    return max(0, savings)


def generate_booking_reference():
    """Generate a unique booking reference"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(4).upper()
    return f"ECO{timestamp}{random_part}"


def generate_transaction_id():
    """Generate a unique transaction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(6).upper()
    return f"TXN{timestamp}{random_part}"


def generate_secure_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def hash_sensitive_data(data):
    """Hash sensitive data using SHA-256"""
    return hashlib.sha256(data.encode()).hexdigest()


def format_currency(amount, currency_symbol='₹'):
    """Format currency amount"""
    if amount is None:
        return f"{currency_symbol}0"
    
    # Format with commas for thousands
    formatted = f"{amount:,.2f}"
    return f"{currency_symbol}{formatted}"


def format_distance(distance_km):
    """Format distance for display"""
    if distance_km < 1:
        return f"{int(distance_km * 1000)}m"
    elif distance_km < 10:
        return f"{distance_km:.1f}km"
    else:
        return f"{int(distance_km)}km"


def format_duration(minutes):
    """Format duration for display"""
    if minutes < 60:
        return f"{int(minutes)} min"
    
    hours = minutes // 60
    remaining_minutes = minutes % 60
    
    if remaining_minutes == 0:
        return f"{int(hours)}h"
    else:
        return f"{int(hours)}h {int(remaining_minutes)}m"


def get_time_ago(datetime_obj):
    """Get human-readable time ago string"""
    now = timezone.now()
    diff = now - datetime_obj
    
    if diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"


def send_notification_email(user, subject, message, html_message=None):
    """Send notification email to user"""
    try:
        send_mail(
            subject=f"EcoCarpool - {subject}",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        # Log error in production
        print(f"Email sending failed: {e}")
        return False


def generate_password_reset_token(user):
    """Generate password reset token"""
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    return uid, token


def validate_business_hours(time_obj, start_hour=6, end_hour=23):
    """Check if time is within business hours"""
    hour = time_obj.hour
    return start_hour <= hour <= end_hour


def get_next_business_day(date_obj=None):
    """Get next business day (Monday-Friday)"""
    if date_obj is None:
        date_obj = timezone.now().date()
    
    next_day = date_obj + timedelta(days=1)
    
    # If it's Saturday (5) or Sunday (6), move to Monday
    while next_day.weekday() >= 5:
        next_day += timedelta(days=1)
    
    return next_day


def sanitize_filename(filename):
    """Sanitize filename for safe storage"""
    import re
    
    # Remove or replace unsafe characters
    filename = re.sub(r'[^\w\s.-]', '', filename)
    filename = re.sub(r'[-\s]+', '-', filename)
    
    return filename.strip('-')


def generate_qr_code_data(booking):
    """Generate QR code data for booking"""
    data = {
        'booking_id': booking.id,
        'reference': booking.reference if hasattr(booking, 'reference') else '',
        'passenger': booking.passenger.get_full_name(),
        'ride_date': booking.ride.ride_date.isoformat(),
        'pickup': booking.ride.start_location,
        'destination': booking.ride.end_location,
    }
    
    import json
    return json.dumps(data)


class RateLimiter:
    """Simple rate limiter for API endpoints"""
    
    def __init__(self, max_requests=100, time_window=3600):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = {}
    
    def is_allowed(self, identifier):
        """Check if request is allowed for identifier"""
        now = timezone.now().timestamp()
        
        # Clean old entries
        self.requests = {
            k: v for k, v in self.requests.items() 
            if now - v['first_request'] < self.time_window
        }
        
        if identifier not in self.requests:
            self.requests[identifier] = {
                'count': 1,
                'first_request': now
            }
            return True
        
        request_data = self.requests[identifier]
        
        if now - request_data['first_request'] >= self.time_window:
            # Reset window
            self.requests[identifier] = {
                'count': 1,
                'first_request': now
            }
            return True
        
        if request_data['count'] >= self.max_requests:
            return False
        
        request_data['count'] += 1
        return True
