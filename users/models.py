from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLES = [
        ('driver', 'Driver'), 
        ('passenger', 'Passenger'),
        ('admin', 'Admin')
    ]
    
    phone = models.CharField(
        max_length=20,
        unique=True
    )
    role = models.CharField(
        max_length=10, 
        choices=ROLES, 
        default='passenger'
    )
    license_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-date_joined']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"