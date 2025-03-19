from django.db import models
from users.models import CustomUser
from vehicles.models import Vehicle

class Location(models.Model):
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.address

class Ride(models.Model):
    driver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='rides')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    start_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='start_rides')
    end_location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='end_rides')
    ride_date = models.DateTimeField()
    available_seats = models.PositiveIntegerField(default=4)
    price_per_seat = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, choices=[('upcoming', 'Upcoming'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], default='upcoming')

    def __str__(self):
        return f"Ride from {self.start_location} to {self.end_location}"