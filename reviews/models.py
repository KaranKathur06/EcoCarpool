from django.db import models
from users.models import CustomUser
from bookings.models import Booking

class Review(models.Model):
    RATING_CHOICES = [(i, i) for i in range(1, 6)]
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    review_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.email} for Booking #{self.booking.id}"