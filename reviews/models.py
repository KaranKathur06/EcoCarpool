from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_given'
    )
    reviewed = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews_received'
    )
    booking = models.OneToOneField(
        'rides.Booking',
        on_delete=models.CASCADE,
        related_name='review'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['reviewer', 'booking']

    def __str__(self):
        return f"Review by {self.reviewer} for {self.reviewed}"