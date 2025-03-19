from django.db import models
from users.models import CustomUser
from rides.models import Ride
from django.conf import settings

class Booking(models.Model):
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]
    #user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ride = models.ForeignKey(Ride, on_delete=models.CASCADE)
    seats_booked = models.PositiveIntegerField(default=1)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='confirmed')

    def __str__(self):
        return f"Booking #{self.id} by {self.user.email}"