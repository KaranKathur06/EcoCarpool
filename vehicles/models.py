# vehicles/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import CustomUser
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from utils.validators import validate_license_plate, validate_file_size, validate_document_file
import uuid

class VehicleType(models.Model):
    CATEGORY_CHOICES = [
        ('Luxury', 'Luxury'),
        ('Mainstream', 'Mainstream'),
        ('Sports', 'Sports'),
        ('Alternative', 'Alternative'),
    ]

    type_name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Mainstream')
    is_popular = models.BooleanField(default=False)

    def __str__(self):
        return self.type_name

    class Meta:
        ordering = ['category', 'type_name']
        # db_table = 'vehicles_vehicletype'  # Uncomment if you want to force table name

class VehicleCompany(models.Model):
    company_name = models.CharField(max_length=100, unique=True)
    is_luxury = models.BooleanField(default=False)
    country_of_origin = models.CharField(max_length=100, blank=True, null=True)
    parent_company = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.company_name

    class Meta:
        ordering = ['company_name']
        verbose_name_plural = "Vehicle Companies"
        # db_table = 'vehicles_vehiclecompany'  # Uncomment if you want to force table name

class VehicleModel(models.Model):
    model_name = models.CharField(max_length=100)
    company = models.ForeignKey(VehicleCompany, on_delete=models.CASCADE, related_name='models', null=True)
    type = models.ForeignKey(VehicleType, on_delete=models.CASCADE, related_name='models', null=True)
    year_from = models.IntegerField(
        default=2000,
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year + 1)
        ]
    )
    year_to = models.IntegerField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(timezone.now().year + 1)
        ]
    )
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    drive_type = models.CharField(max_length=50, blank=True, null=True)
    body_style = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.company.company_name if self.company else ''} {self.model_name}"

    class Meta:
        ordering = ['company__company_name', 'model_name']
        unique_together = ['company', 'model_name']
        # db_table = 'vehicles_vehiclemodel'  # Uncomment if you want to force table name

class Vehicle(models.Model):
    FUEL_TYPE_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('plug_in_hybrid', 'Plug-in Hybrid'),
        ('hydrogen', 'Hydrogen'),
        ('cng', 'CNG'),
        ('lpg', 'LPG'),
    ]
    
    CONDITION_CHOICES = [
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    company = models.ForeignKey(VehicleCompany, on_delete=models.PROTECT)
    model = models.ForeignKey(VehicleModel, on_delete=models.PROTECT)
    license_plate = models.CharField(max_length=20, unique=True, validators=[validate_license_plate])
    color = models.CharField(max_length=50)
    year = models.IntegerField(
        validators=[
            MinValueValidator(1990),
            MaxValueValidator(timezone.now().year + 1)
        ]
    )
    seating_capacity = models.IntegerField(
        validators=[
            MinValueValidator(2),
            MaxValueValidator(10)
        ]
    )
    fuel_type = models.CharField(max_length=20, choices=FUEL_TYPE_CHOICES, default='petrol')
    mileage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="km/l or km/kWh")
    odometer_reading = models.PositiveIntegerField(null=True, blank=True, help_text="Total kilometers driven")
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    vehicle_photo = models.ImageField(upload_to='vehicle_photos/', null=True, blank=True)
    additional_photos = models.JSONField(default=list, blank=True, help_text="List of additional photo URLs")
    features = models.JSONField(default=list, blank=True, help_text="List of vehicle features")
    description = models.TextField(blank=True, max_length=500)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_available_for_rides = models.BooleanField(default=True)
    insurance_expiry = models.DateField(null=True, blank=True)
    registration_expiry = models.DateField(null=True, blank=True)
    pollution_certificate_expiry = models.DateField(null=True, blank=True)
    last_service_date = models.DateField(null=True, blank=True)
    next_service_due = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', 'is_active']),
            models.Index(fields=['is_verified', 'is_active']),
            models.Index(fields=['license_plate']),
        ]

    def __str__(self):
        return f"{self.company.company_name} {self.model.model_name} - {self.license_plate}"

    def clean(self):
        if self.year > timezone.now().year + 1:
            raise ValidationError("Vehicle year cannot be in the future.")
        
        if self.insurance_expiry and self.insurance_expiry <= timezone.now().date():
            raise ValidationError("Insurance must be valid.")
        
        if self.registration_expiry and self.registration_expiry <= timezone.now().date():
            raise ValidationError("Registration must be valid.")

    def save(self, *args, **kwargs):
        self.license_plate = self.license_plate.upper()
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_documents_valid(self):
        """Check if all required documents are valid"""
        today = timezone.now().date()
        return (
            (not self.insurance_expiry or self.insurance_expiry > today) and
            (not self.registration_expiry or self.registration_expiry > today) and
            (not self.pollution_certificate_expiry or self.pollution_certificate_expiry > today)
        )

    @property
    def needs_service(self):
        """Check if vehicle needs service"""
        if not self.next_service_due:
            return False
        return self.next_service_due <= timezone.now().date()

    def get_total_rides(self):
        """Get total number of rides for this vehicle"""
        return self.rides.count()

    def get_total_earnings(self):
        """Get total earnings from rides with this vehicle"""
        from django.db.models import Sum, F
        return self.rides.filter(
            status='completed'
        ).aggregate(
            total=Sum(F('bookings__seats') * F('price_per_seat'))
        )['total'] or 0

    def get_average_rating(self):
        """Get average rating for rides with this vehicle"""
        from django.db.models import Avg
        return self.rides.filter(
            reviews__isnull=False
        ).aggregate(
            avg_rating=Avg('reviews__rating')
        )['avg_rating'] or 0

    def get_fuel_efficiency_display(self):
        """Get formatted fuel efficiency display"""
        if not self.mileage:
            return "Not specified"
        
        if self.fuel_type == 'electric':
            return f"{self.mileage} km/kWh"
        else:
            return f"{self.mileage} km/l"

    def get_condition_badge_class(self):
        """Get CSS class for condition badge"""
        condition_classes = {
            'excellent': 'badge-success',
            'good': 'badge-primary',
            'fair': 'badge-warning',
            'poor': 'badge-danger',
        }
        return condition_classes.get(self.condition, 'badge-secondary')

class VehicleDocument(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ('registration', 'Registration Certificate'),
        ('insurance', 'Insurance Document'),
        ('pollution', 'Pollution Certificate'),
        ('license', 'Driving License'),
        ('permit', 'Commercial Permit'),
        ('fitness', 'Fitness Certificate'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_number = models.CharField(max_length=50, blank=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    document_file = models.FileField(
        upload_to='vehicle_documents/', 
        validators=[validate_document_file, validate_file_size]
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='verified_documents'
    )
    verified_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['vehicle', 'document_type']
        indexes = [
            models.Index(fields=['status', 'document_type']),
            models.Index(fields=['expiry_date']),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.get_document_type_display()}"

    def clean(self):
        if self.expiry_date and self.issue_date:
            if self.expiry_date <= self.issue_date:
                raise ValidationError("Expiry date must be after issue date.")
        
        if self.expiry_date and self.expiry_date <= timezone.now().date():
            self.status = 'expired'

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if document is expired"""
        if not self.expiry_date:
            return False
        return self.expiry_date <= timezone.now().date()

    @property
    def days_until_expiry(self):
        """Get days until document expires"""
        if not self.expiry_date:
            return None
        delta = self.expiry_date - timezone.now().date()
        return delta.days

    @property
    def is_expiring_soon(self):
        """Check if document expires within 30 days"""
        days = self.days_until_expiry
        return days is not None and 0 <= days <= 30

    def get_status_badge_class(self):
        """Get CSS class for status badge"""
        status_classes = {
            'pending': 'badge-warning',
            'verified': 'badge-success',
            'rejected': 'badge-danger',
            'expired': 'badge-dark',
        }
        return status_classes.get(self.status, 'badge-secondary')


class VehicleMaintenanceRecord(models.Model):
    """Track vehicle maintenance history"""
    MAINTENANCE_TYPE_CHOICES = [
        ('service', 'Regular Service'),
        ('repair', 'Repair'),
        ('inspection', 'Inspection'),
        ('oil_change', 'Oil Change'),
        ('tire_change', 'Tire Change'),
        ('brake_service', 'Brake Service'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_records')
    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_TYPE_CHOICES)
    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    service_provider = models.CharField(max_length=200, blank=True)
    odometer_reading = models.PositiveIntegerField(help_text="Odometer reading at time of service")
    service_date = models.DateField()
    next_service_due = models.DateField(null=True, blank=True)
    receipt_file = models.FileField(upload_to='maintenance_receipts/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-service_date']
        indexes = [
            models.Index(fields=['vehicle', 'service_date']),
            models.Index(fields=['maintenance_type']),
        ]

    def __str__(self):
        return f"{self.vehicle} - {self.get_maintenance_type_display()} on {self.service_date}"