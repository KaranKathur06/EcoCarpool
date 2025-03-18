# bookings/models.py
from django.db import models
from django.core.validators import MinValueValidator , MaxValueValidator
from users.models import User
from rides.models import Ride

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    max_usage = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-valid_from']

    def __str__(self):
        return f"{self.code} ({self.discount_percent}%)"

class Booking(models.Model):
    passenger = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    ride = models.ForeignKey(
        Ride,
        on_delete=models.CASCADE,
        related_name='bookings'
    )
    seats_booked = models.PositiveIntegerField(default=1)
    # Rest of fields remain same...

class Payment(models.Model):
    # Keep existing fields but add:
    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'
        ordering = ['-initiated_at']
        get_latest_by = 'initiated_at'  