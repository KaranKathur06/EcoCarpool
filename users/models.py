from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from datetime import timedelta
from django.db.models import Count, Sum, Avg

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('driver', 'Driver'),
        ('passenger', 'Passenger'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='passenger')
    
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 10 digits allowed."
    )
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True)
    
    address = models.TextField(blank=True)
    
    bio = models.TextField(blank=True)
    
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    
    registration_date = models.DateTimeField(default=timezone.now)
    
    is_verified = models.BooleanField(default=False)
    
    def get_profile_picture_url(self):
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-profile.png'
    
    @property
    def is_admin(self):
        return self.role == 'admin'
    
    @property
    def is_driver(self):
        return self.role == 'driver'
    
    @property
    def is_passenger(self):
        return self.role == 'passenger'
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name or self.last_name else self.username
    
    def get_role_display_name(self):
        """Get the display name for the user's role"""
        if not self.role:
            return 'Not Set'
        return dict(self.ROLE_CHOICES).get(self.role, 'Unknown')
    
    def get_total_users(self):
        if self.is_admin:
            return CustomUser.objects.count()
        return None
    
    def get_total_drivers(self):
        if self.is_admin:
            return CustomUser.objects.filter(role='driver').count()
        return None
    
    def get_total_passengers(self):
        if self.is_admin:
            return CustomUser.objects.filter(role='passenger').count()
        return None
    
    def get_total_rides(self):
        from rides.models import Ride
        if self.is_admin:
            return Ride.objects.count()
        elif self.role == 'driver':
            return self.driver_rides.count()
        else:
            return self.bookings.count()
    
    def get_total_earnings_all_drivers(self):
        if self.is_admin:
            from rides.models import Booking
            completed_bookings = Booking.objects.filter(status='completed')
            return sum(booking.get_total_price() for booking in completed_bookings)
        return None
    
    def get_platform_statistics(self):
        if self.is_admin:
            from rides.models import Ride, Booking
            return {
                'total_rides': Ride.objects.count(),
                'completed_rides': Ride.objects.filter(status='completed').count(),
                'active_rides': Ride.objects.filter(status='active').count(),
                'total_earnings': self.get_total_earnings_all_drivers(),
                'total_users': self.get_total_users(),
                'total_drivers': self.get_total_drivers(),
                'total_passengers': self.get_total_passengers(),
                'average_rating': self.get_average_platform_rating()
            }
        return None
    
    def get_average_platform_rating(self):
        if self.is_admin:
            Review = apps.get_model('reviews', 'Review')
            reviews = Review.objects.all()
            if reviews.exists():
                return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    def get_rating(self):
        Review = apps.get_model('reviews', 'Review')
        reviews = Review.objects.filter(reviewed=self)
        if reviews.exists():
            return reviews.aggregate(models.Avg('rating'))['rating__avg']
        return 0
    
    def __str__(self):
        return self.username
    
    def get_rides_as_driver(self):
        if self.role == 'driver':
            return self.driver_rides.all()
        return None
    
    def get_bookings_as_passenger(self):
        if self.role == 'passenger':
            return self.bookings.all()
        return None
    
    def get_total_earnings(self):
        from rides.models import Booking
        completed_bookings = Booking.objects.filter(
            ride__driver=self,
            status='completed'
        )
        return sum(booking.get_total_price() for booking in completed_bookings)
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def get_today_earnings(self):
        if self.role == 'driver':
            from rides.models import Booking
            today = timezone.now().date()
            completed_bookings = Booking.objects.filter(
                ride__driver=self,
                status='completed',
                updated_at__date=today
            )
            return sum(booking.get_total_price() for booking in completed_bookings)
        return 0

    def get_week_rides(self):
        if self.role == 'driver':
            week_ago = timezone.now() - timedelta(days=7)
            return self.driver_rides.filter(created_at__gte=week_ago).count()
        return 0

    def get_today_passengers(self):
        if self.role == 'driver':
            today = timezone.now().date()
            return self.driver_rides.filter(
                created_at__date=today
            ).aggregate(
                total=Count('bookings')
            )['total'] or 0
        return 0

    def get_total_savings(self):
        if self.role == 'passenger':
            from rides.models import Booking
            completed_bookings = Booking.objects.filter(
                passenger=self,
                status='completed'
            )
            # Assuming 30% savings compared to regular taxi fare
            return sum(booking.get_total_price() * 0.3 for booking in completed_bookings)
        return 0

    def get_co2_reduction(self):
        if self.role == 'passenger':
            completed_rides = self.bookings.filter(status='completed').count()
            # Assuming 2.3kg CO2 saved per shared ride
            return completed_rides * 2.3
        return 0

    def get_favorite_routes_count(self):
        """Get the count of favorite routes for a passenger"""
        if self.role == 'passenger':
            from rides.models import Booking
            return Booking.objects.filter(
                passenger=self
            ).values(
                'ride__start_location',
                'ride__end_location'
            ).annotate(
                count=Count('id')
            ).filter(count__gt=1).count()
        return 0

    @classmethod
    def get_user_growth_data(cls, period='week'):
        today = timezone.now().date()
        if period == 'week':
            start_date = today - timedelta(days=7)
            date_format = '%a'
        elif period == 'month':
            start_date = today - timedelta(days=30)
            date_format = '%d %b'
        else:  # year
            start_date = today - timedelta(days=365)
            date_format = '%b'

        return cls.objects.filter(
            date_joined__date__gte=start_date
        ).extra(
            select={'date': "DATE_FORMAT(date_joined, %s)"},
            select_params=(date_format,)
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date_joined')

    @classmethod
    def get_platform_statistics(cls):
        from rides.models import Ride, Booking
        today = timezone.now().date()
        
        # User statistics
        total_users = cls.objects.count()
        new_users = cls.objects.filter(date_joined__date=today).count()
        drivers = cls.objects.filter(role='driver').count()
        passengers = cls.objects.filter(role='passenger').count()
        
        # Ride statistics
        total_rides = Ride.objects.count()
        active_rides = Ride.objects.filter(status='active').count()
        completed_rides = Ride.objects.filter(status='completed').count()
        
        # Earnings statistics
        completed_bookings = Booking.objects.filter(status='completed')
        total_earnings = completed_bookings.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        return {
            'total_users': total_users,
            'new_users': new_users,
            'drivers': drivers,
            'passengers': passengers,
            'total_rides': total_rides,
            'active_rides': active_rides,
            'completed_rides': completed_rides,
            'total_earnings': total_earnings,
            'average_rating': cls.get_average_platform_rating()
        }

    @classmethod
    def get_average_platform_rating(cls):
        from reviews.models import Review
        return Review.objects.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0