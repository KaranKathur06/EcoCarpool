from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import CustomUser
from vehicles.models import Vehicle
from utils.helpers import calculate_distance, generate_booking_reference
import uuid

class Location(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'rides_location'

    def __str__(self):
        return self.address

class Ride(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('full', 'Full'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='driver_rides')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_latitude = models.FloatField(null=True, blank=True)
    start_longitude = models.FloatField(null=True, blank=True)
    end_latitude = models.FloatField(null=True, blank=True)
    end_longitude = models.FloatField(null=True, blank=True)
    ride_date = models.DateTimeField()
    available_seats = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(8)])
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_duration = models.PositiveIntegerField(null=True, blank=True, help_text="Duration in minutes")
    description = models.TextField(blank=True, max_length=500)
    is_recurring = models.BooleanField(default=False)
    recurring_days = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_instant_booking = models.BooleanField(default=False)
    smoking_allowed = models.BooleanField(default=False)
    pets_allowed = models.BooleanField(default=False)
    luggage_allowed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'rides_ride'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'ride_date']),
            models.Index(fields=['driver', 'status']),
        ]

    def __str__(self):
        return f"Ride from {self.start_location} to {self.end_location} on {self.ride_date.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        if self.ride_date and self.ride_date <= timezone.now():
            raise ValidationError("Ride date must be in the future.")
        
        if self.start_location == self.end_location:
            raise ValidationError("Start and end locations cannot be the same.")
        
        if self.vehicle and self.vehicle.owner != self.driver:
            raise ValidationError("Driver must own the selected vehicle.")

    def save(self, *args, **kwargs):
        self.clean()
        
        # Calculate distance if coordinates are provided
        if all([self.start_latitude, self.start_longitude, self.end_latitude, self.end_longitude]):
            try:
                self.distance = calculate_distance(
                    self.start_latitude, self.start_longitude,
                    self.end_latitude, self.end_longitude
                )
            except:
                pass
        
        super().save(*args, **kwargs)

    def get_total_price(self):
        return self.price_per_seat * self.available_seats

    def get_booked_seats(self):
        return self.bookings.filter(status__in=['confirmed', 'completed']).aggregate(
            total=models.Sum('seats')
        )['total'] or 0

    def get_available_seats_count(self):
        return self.available_seats - self.get_booked_seats()

    def is_full(self):
        return self.get_available_seats_count() <= 0

    def can_book(self):
        return (
            self.status in ['active', 'draft'] and 
            not self.is_full() and 
            self.ride_date > timezone.now()
        )

    def get_earnings(self):
        """Calculate total earnings from confirmed bookings"""
        return self.bookings.filter(status__in=['confirmed', 'completed']).aggregate(
            total=models.Sum(models.F('seats') * models.F('ride__price_per_seat'))
        )['total'] or 0

    def get_co2_savings(self):
        """Calculate CO2 savings from this ride"""
        from utils.helpers import calculate_co2_savings
        if self.distance:
            return calculate_co2_savings(float(self.distance), self.get_booked_seats())
        return 0

    @property
    def is_past(self):
        return self.ride_date <= timezone.now()

    @property
    def is_today(self):
        return self.ride_date.date() == timezone.now().date()

    def get_status_display_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'draft': 'badge-secondary',
            'active': 'badge-primary',
            'full': 'badge-warning',
            'started': 'badge-info',
            'completed': 'badge-success',
            'cancelled': 'badge-danger',
        }
        return status_classes.get(self.status, 'badge-secondary')

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    seats = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    pickup_location = models.CharField(max_length=255, blank=True)
    dropoff_location = models.CharField(max_length=255, blank=True)
    special_requests = models.TextField(blank=True, max_length=200)
    payment_status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('refunded', 'Refunded'),
        ('failed', 'Failed'),
    ], default='pending')
    payment_method = models.CharField(max_length=20, choices=[
        ('wallet', 'Wallet'),
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('cash', 'Cash'),
    ], blank=True)
    cancellation_reason = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_bookings')
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rides_booking'
        unique_together = ['ride', 'passenger']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['passenger', 'status']),
            models.Index(fields=['booking_reference']),
        ]

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.passenger.username} on {self.ride}"

    def clean(self):
        if self.seats > self.ride.get_available_seats_count():
            raise ValidationError("Not enough seats available for this booking.")
        
        if self.ride.driver == self.passenger:
            raise ValidationError("Driver cannot book their own ride.")
        
        if self.ride.ride_date <= timezone.now():
            raise ValidationError("Cannot book a ride in the past.")

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = generate_booking_reference()
        
        self.clean()
        super().save(*args, **kwargs)

    def get_total_price(self):
        return self.ride.price_per_seat * self.seats

    def can_cancel(self):
        """Check if booking can be cancelled"""
        if self.status in ['cancelled', 'completed', 'no_show']:
            return False
        
        # Allow cancellation up to 2 hours before ride
        time_until_ride = self.ride.ride_date - timezone.now()
        return time_until_ride.total_seconds() > 7200  # 2 hours

    def cancel(self, cancelled_by, reason=""):
        """Cancel the booking"""
        if not self.can_cancel():
            raise ValidationError("This booking cannot be cancelled.")
        
        self.status = 'cancelled'
        self.cancelled_by = cancelled_by
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()

    def get_status_display_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'pending': 'badge-warning',
            'confirmed': 'badge-success',
            'cancelled': 'badge-danger',
            'completed': 'badge-primary',
            'no_show': 'badge-dark',
        }
        return status_classes.get(self.status, 'badge-secondary')

    @property
    def is_active(self):
        return self.status in ['pending', 'confirmed']

    @property
    def refund_amount(self):
        """Calculate refund amount based on cancellation time"""
        if self.status != 'cancelled':
            return 0
        
        total_price = self.get_total_price()
        time_until_ride = self.ride.ride_date - self.cancelled_at
        hours_until_ride = time_until_ride.total_seconds() / 3600
        
        if hours_until_ride >= 24:
            return total_price  # Full refund
        elif hours_until_ride >= 12:
            return total_price * 0.75  # 75% refund
        elif hours_until_ride >= 2:
            return total_price * 0.50  # 50% refund
        else:
            return 0  # No refund


class RideRequest(models.Model):
    """Model for passengers to request rides on specific routes"""
    passenger = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='ride_requests')
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    start_latitude = models.FloatField(null=True, blank=True)
    start_longitude = models.FloatField(null=True, blank=True)
    end_latitude = models.FloatField(null=True, blank=True)
    end_longitude = models.FloatField(null=True, blank=True)
    preferred_date = models.DateTimeField()
    max_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    seats_needed = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    description = models.TextField(blank=True, max_length=300)
    is_flexible = models.BooleanField(default=True, help_text="Flexible with timing")
    status = models.CharField(max_length=20, choices=[
        ('active', 'Active'),
        ('matched', 'Matched'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
    ], default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'rides_riderequest'
        ordering = ['-created_at']

    def __str__(self):
        return f"Ride request from {self.start_location} to {self.end_location} by {self.passenger.username}"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Expire after 7 days
            self.expires_at = timezone.now() + timezone.timedelta(days=7)
        super().save(*args, **kwargs)