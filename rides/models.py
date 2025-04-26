from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from users.models import CustomUser
from vehicles.models import Vehicle

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
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True, related_name='driver_rides')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.SET_NULL, null=True, blank=True)
    start_location = models.CharField(max_length=255)
    end_location = models.CharField(max_length=255)
    ride_date = models.DateTimeField()
    available_seats = models.IntegerField(validators=[MinValueValidator(1)])
    price_per_seat = models.DecimalField(max_digits=10, decimal_places=2)
    distance = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    estimated_duration = models.BigIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    is_recurring = models.BooleanField(default=False)
    recurring_days = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'rides_ride'

    def __str__(self):
        return f"Ride from {self.start_location} to {self.end_location} on {self.ride_date}"

    def get_total_price(self):
        return self.price_per_seat * self.available_seats

    def get_booked_seats(self):
        return self.bookings.filter(status='confirmed').count()

    def get_available_seats_count(self):
        return self.available_seats - self.get_booked_seats()

    def is_full(self):
        return self.get_available_seats_count() == 0

    def can_book(self):
        return self.status == 'pending' and not self.is_full()

class Booking(models.Model):
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name='bookings')
    passenger = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    seats = models.IntegerField(validators=[MinValueValidator(1)])
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rides_booking'
        unique_together = ['ride', 'passenger']

    def __str__(self):
        return f"Booking for {self.passenger} on {self.ride}"

    def get_total_price(self):
        return self.ride.price_per_seat * self.seats