# vehicles/models.py
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from users.models import CustomUser
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class VehicleType(models.Model):
    type_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.type_name

    class Meta:
        db_table = 'vehicle_type'

class VehicleCompany(models.Model):
    company_name = models.CharField(max_length=100)
    is_luxury = models.BooleanField(default=False)
    country_of_origin = models.CharField(max_length=100)

    def __str__(self):
        return self.company_name

    class Meta:
        db_table = 'vehicle_company'
        verbose_name_plural = 'Vehicle Companies'

class VehicleModel(models.Model):
    model_name = models.CharField(max_length=100)
    company = models.ForeignKey(VehicleCompany, on_delete=models.CASCADE)
    type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
    year_from = models.IntegerField()
    year_to = models.IntegerField(null=True, blank=True)
    base_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.company.company_name} {self.model_name} ({self.year_from})"

    class Meta:
        db_table = 'vehicle_model'

class Vehicle(models.Model):
    FUEL_CHOICES = [
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
        ('cng', 'CNG'),
        ('lpg', 'LPG'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey(VehicleCompany, on_delete=models.CASCADE, null=True)
    model = models.ForeignKey(VehicleModel, on_delete=models.CASCADE, null=True)
    license_plate = models.CharField(max_length=20, unique=True)
    color = models.CharField(max_length=50)
    year = models.PositiveIntegerField()
    seating_capacity = models.PositiveIntegerField()
    fuel_type = models.CharField(max_length=20, choices=FUEL_CHOICES, default='petrol')
    mileage = models.DecimalField(max_digits=5, decimal_places=2, help_text="Mileage in km/l", null=True, blank=True)
    vehicle_photo = models.ImageField(upload_to='vehicle_photos/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.company} {self.model} - {self.license_plate}"

    class Meta:
        ordering = ['-created_at']

class VehicleDocument(models.Model):
    DOCUMENT_TYPES = [
        ('registration', 'Vehicle Registration'),
        ('insurance', 'Insurance'),
        ('permit', 'Permit'),
        ('pollution', 'Pollution Certificate'),
        ('other', 'Other')
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    document_file = models.FileField(upload_to='vehicle_documents/')
    expiry_date = models.DateField(null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.vehicle.license_plate} - {self.get_document_type_display()}"

    class Meta:
        ordering = ['-uploaded_at']

    def clean(self):
        if self.document_file:
            # Check file extension
            ext = self.document_file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise ValidationError({
                    'document_file': _('Only PDF and Word documents are allowed.')
                })

            # Check file size (5MB limit)
            if self.document_file.size > 5 * 1024 * 1024:
                raise ValidationError({
                    'document_file': _('File size must be no more than 5MB.')
                })

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)