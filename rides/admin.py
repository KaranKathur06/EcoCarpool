from django.contrib import admin
from .models import Ride, Location

@admin.register(Ride)
class RideAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'start_location',
        'end_location',
        'ride_date',
        'available_seats',
        'price_per_seat',
        'status'
    ]
    list_filter = ['status', 'ride_date', 'is_recurring']
    search_fields = ['start_location', 'end_location', 'description']
    readonly_fields = ['created_at']

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('address', 'latitude', 'longitude')