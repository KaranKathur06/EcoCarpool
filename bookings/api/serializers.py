from rest_framework import serializers
from ..models import Booking

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['id', 'user', 'ride', 'seats_booked', 'status', 'booking_date']