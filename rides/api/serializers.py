from rest_framework import serializers
from ..models import Ride, Location

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'address', 'latitude', 'longitude']

class RideSerializer(serializers.ModelSerializer):
    start_location = LocationSerializer()
    end_location = LocationSerializer()
    
    class Meta:
        model = Ride
        fields = ['id', 'driver', 'vehicle', 'start_location', 'end_location', 'ride_date', 'available_seats', 'price_per_seat', 'status']