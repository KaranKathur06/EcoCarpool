# vehicles/models.py
from django.db import models
from users.models import CustomUser

class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('hatchback', 'Hatchback'),
        ('sedan', 'Sedan'),
        ('suv', 'SUV'),
        ('electric', 'Electric Vehicle'),
    ]
    
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='vehicles')
    license_plate = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPES)
    model = models.CharField(max_length=50)
    color = models.CharField(max_length=20)
    seats_available = models.PositiveIntegerField(default=4)

    def __str__(self):
        return f"{self.model} ({self.license_plate})"