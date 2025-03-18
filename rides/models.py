from django.db import models
from django.core.validators import MinValueValidator
from users.models import User
from vehicles.models import Vehicle

class Ride(models.Model):
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ]
    
    driver = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='rides_offered'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.CASCADE,
        related_name='rides'
    )
    start_point = models.CharField(max_length=255)
    end_point = models.CharField(max_length=255)
    departure_time = models.DateTimeField()  # Renamed from start_time
    available_seats = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    status = models.CharField(
        max_length=10, 
        choices=STATUS_CHOICES, 
        default='scheduled'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-departure_time']
        indexes = [
            models.Index(fields=['departure_time']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.departure_time} - {self.start_point} to {self.end_point}"

class SOSAlert(models.Model):
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='alerts'
    )
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10, 
        choices=[('active', 'Active'), ('resolved', 'Resolved')],
        default='active'
    )

class CarbonFootprint(models.Model):
    ride = models.OneToOneField(
        Ride,
        on_delete=models.CASCADE,
        related_name='carbon_footprint'
    )
    distance_km = models.DecimalField(
        max_digits=6, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    co2_saved_kg = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )