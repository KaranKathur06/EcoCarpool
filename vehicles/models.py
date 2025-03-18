# vehicles/models.py
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import User

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('hatchback', 'Hatchback'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('electric', 'Electric Vehicle'),
    ]
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    license_plate = models.CharField(
        max_length=20, 
        unique=True
    )
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1990),
            MaxValueValidator(2025)
        ]
    )
    color = models.CharField(max_length=50)
    seating_capacity = models.PositiveIntegerField(
        validators=[MinValueValidator(2)]
    )
    vehicle_type = models.CharField(
        max_length=20,
        choices=VEHICLE_TYPES
    )

    class Meta:
        verbose_name = 'Vehicle'
        verbose_name_plural = 'Vehicles'

    def __str__(self):
        return f"{self.year} {self.make} {self.model} ({self.license_plate})"