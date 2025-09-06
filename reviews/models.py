from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
import uuid

class Review(models.Model):
    REVIEW_TYPE_CHOICES = [
        ('driver_to_passenger', 'Driver to Passenger'),
        ('passenger_to_driver', 'Passenger to Driver'),
    ]
    
    ASPECT_CHOICES = [
        ('punctuality', 'Punctuality'),
        ('communication', 'Communication'),
        ('cleanliness', 'Cleanliness'),
        ('driving_skill', 'Driving Skill'),
        ('friendliness', 'Friendliness'),
        ('vehicle_condition', 'Vehicle Condition'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    ride = models.ForeignKey(
        'rides.Ride',
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    booking = models.ForeignKey(
        'rides.Booking',
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    review_type = models.CharField(
        max_length=25,
        choices=REVIEW_TYPE_CHOICES,
        default='passenger_to_driver'
    )
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(max_length=1000)
    aspects = models.JSONField(default=dict, blank=True, help_text="Ratings for specific aspects")
    is_anonymous = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    reported_count = models.PositiveIntegerField(default=0)
    is_verified = models.BooleanField(default=True)
    response = models.TextField(blank=True, max_length=500, help_text="Response from reviewed user")
    response_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['reviewer', 'ride', 'review_type']
        indexes = [
            models.Index(fields=['reviewed', 'rating']),
            models.Index(fields=['ride', 'review_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.get_review_type_display()} - {self.rating}★ by {self.reviewer.username}"

    def clean(self):
        # Validate that reviewer and reviewed are different
        if self.reviewer == self.reviewed:
            raise ValidationError("You cannot review yourself.")
        
        # Validate review type based on ride relationship
        if self.review_type == 'driver_to_passenger':
            if self.ride.driver != self.reviewer:
                raise ValidationError("Only the driver can review passengers.")
            if self.booking and self.booking.passenger != self.reviewed:
                raise ValidationError("Invalid passenger for this review.")
        
        elif self.review_type == 'passenger_to_driver':
            if self.ride.driver != self.reviewed:
                raise ValidationError("You can only review the driver of this ride.")
            if self.booking and self.booking.passenger != self.reviewer:
                raise ValidationError("Only passengers can review the driver.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def can_respond(self):
        """Check if the reviewed user can respond to this review"""
        return not self.response and self.reviewed

    def add_response(self, response_text):
        """Add a response to the review"""
        if self.can_respond:
            self.response = response_text
            self.response_date = timezone.now()
            self.save()

    def get_rating_stars(self):
        """Get star representation of rating"""
        return '★' * self.rating + '☆' * (5 - self.rating)

    def get_aspect_ratings(self):
        """Get formatted aspect ratings"""
        if not self.aspects:
            return {}
        
        formatted = {}
        for aspect, rating in self.aspects.items():
            if aspect in dict(self.ASPECT_CHOICES):
                formatted[dict(self.ASPECT_CHOICES)[aspect]] = rating
        return formatted


class ReviewHelpful(models.Model):
    """Track users who found a review helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'user']

    def __str__(self):
        return f"{self.user.username} found review {self.review.id} helpful"


class ReviewReport(models.Model):
    """Track reports on inappropriate reviews"""
    REPORT_REASON_CHOICES = [
        ('inappropriate', 'Inappropriate Content'),
        ('spam', 'Spam'),
        ('fake', 'Fake Review'),
        ('harassment', 'Harassment'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('resolved', 'Resolved'),
        ('dismissed', 'Dismissed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    reason = models.CharField(max_length=20, choices=REPORT_REASON_CHOICES)
    description = models.TextField(max_length=500, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    admin_notes = models.TextField(blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_reports'
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['review', 'reporter']
        ordering = ['-created_at']

    def __str__(self):
        return f"Report on review {self.review.id} by {self.reporter.username}"


class ReviewTemplate(models.Model):
    """Pre-defined review templates for quick reviews"""
    TEMPLATE_TYPE_CHOICES = [
        ('positive', 'Positive'),
        ('neutral', 'Neutral'),
        ('negative', 'Negative'),
    ]

    title = models.CharField(max_length=100)
    content = models.TextField(max_length=500)
    template_type = models.CharField(max_length=10, choices=TEMPLATE_TYPE_CHOICES)
    suggested_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_active = models.BooleanField(default=True)
    usage_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['template_type', 'title']

    def __str__(self):
        return f"{self.title} ({self.get_template_type_display()})"

    def increment_usage(self):
        """Increment usage count when template is used"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])