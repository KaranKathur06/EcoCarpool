from django.db import models
from bookings.models import Booking

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')

    def __str__(self):
        return f"Payment #{self.id} for Booking #{self.booking.id}"