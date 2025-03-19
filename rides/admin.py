from django.contrib import admin
from .models import Ride, Location

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = ('driver', 'start_location', 'end_location', 'ride_date', 'available_seats')

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'latitude', 'longitude')