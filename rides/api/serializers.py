from rest_framework import serializers
from django.utils import timezone
from ..models import Ride, Location, Booking, RideRequest
from users.api.serializers import UserBasicSerializer
from vehicles.api.serializers import VehicleBasicSerializer

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['id', 'address', 'latitude', 'longitude', 'created_at']
        read_only_fields = ['id', 'created_at']

class RideListSerializer(serializers.ModelSerializer):
    """Serializer for ride list view with minimal data"""
    driver = UserBasicSerializer(read_only=True)
    vehicle = VehicleBasicSerializer(read_only=True)
    available_seats_count = serializers.SerializerMethodField()
    booked_seats = serializers.SerializerMethodField()
    is_bookable = serializers.SerializerMethodField()
    co2_savings = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id', 'driver', 'vehicle', 'start_location', 'end_location',
            'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude',
            'ride_date', 'available_seats', 'available_seats_count', 'booked_seats',
            'price_per_seat', 'distance', 'estimated_duration', 'status', 'status_display',
            'is_instant_booking', 'smoking_allowed', 'pets_allowed', 'luggage_allowed',
            'is_bookable', 'co2_savings', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def get_available_seats_count(self, obj):
        return obj.get_available_seats_count()

    def get_booked_seats(self, obj):
        return obj.get_booked_seats()

    def get_is_bookable(self, obj):
        return obj.can_book()

    def get_co2_savings(self, obj):
        return obj.get_co2_savings()

class RideDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single ride view"""
    driver = UserBasicSerializer(read_only=True)
    vehicle = VehicleBasicSerializer(read_only=True)
    bookings = serializers.SerializerMethodField()
    available_seats_count = serializers.SerializerMethodField()
    booked_seats = serializers.SerializerMethodField()
    is_bookable = serializers.SerializerMethodField()
    co2_savings = serializers.SerializerMethodField()
    earnings = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_class = serializers.CharField(source='get_status_display_class', read_only=True)
    is_past = serializers.BooleanField(read_only=True)
    is_today = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Ride
        fields = [
            'id', 'driver', 'vehicle', 'start_location', 'end_location',
            'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude',
            'ride_date', 'available_seats', 'available_seats_count', 'booked_seats',
            'price_per_seat', 'distance', 'estimated_duration', 'description',
            'is_recurring', 'recurring_days', 'status', 'status_display', 'status_class',
            'is_instant_booking', 'smoking_allowed', 'pets_allowed', 'luggage_allowed',
            'is_bookable', 'co2_savings', 'earnings', 'is_past', 'is_today',
            'bookings', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_bookings(self, obj):
        bookings = obj.bookings.filter(status__in=['confirmed', 'pending'])
        return BookingBasicSerializer(bookings, many=True).data

    def get_available_seats_count(self, obj):
        return obj.get_available_seats_count()

    def get_booked_seats(self, obj):
        return obj.get_booked_seats()

    def get_is_bookable(self, obj):
        return obj.can_book()

    def get_co2_savings(self, obj):
        return obj.get_co2_savings()

    def get_earnings(self, obj):
        return obj.get_earnings()

class RideCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating rides"""
    
    class Meta:
        model = Ride
        fields = [
            'vehicle', 'start_location', 'end_location',
            'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude',
            'ride_date', 'available_seats', 'price_per_seat', 'description',
            'is_recurring', 'recurring_days', 'is_instant_booking',
            'smoking_allowed', 'pets_allowed', 'luggage_allowed'
        ]

    def validate_ride_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Ride date must be in the future.")
        return value

    def validate_available_seats(self, value):
        if value < 1 or value > 8:
            raise serializers.ValidationError("Available seats must be between 1 and 8.")
        return value

    def validate_price_per_seat(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price per seat must be greater than 0.")
        return value

    def validate(self, data):
        if data.get('start_location') == data.get('end_location'):
            raise serializers.ValidationError("Start and end locations cannot be the same.")
        
        # Validate vehicle ownership
        request = self.context.get('request')
        if request and data.get('vehicle'):
            if data['vehicle'].owner != request.user:
                raise serializers.ValidationError("You can only create rides with your own vehicles.")
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['driver'] = request.user
        return super().create(validated_data)

class BookingBasicSerializer(serializers.ModelSerializer):
    """Basic booking serializer for nested use"""
    passenger = UserBasicSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_class = serializers.CharField(source='get_status_display_class', read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'passenger', 'seats', 'status', 'status_display', 'status_class',
            'booking_reference', 'pickup_location', 'dropoff_location',
            'total_price', 'created_at'
        ]
        read_only_fields = ['id', 'booking_reference', 'created_at']

    def get_total_price(self, obj):
        return obj.get_total_price()

class BookingDetailSerializer(serializers.ModelSerializer):
    """Detailed booking serializer"""
    ride = RideListSerializer(read_only=True)
    passenger = UserBasicSerializer(read_only=True)
    total_price = serializers.SerializerMethodField()
    can_cancel = serializers.SerializerMethodField()
    refund_amount = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    status_class = serializers.CharField(source='get_status_display_class', read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Booking
        fields = [
            'id', 'ride', 'passenger', 'seats', 'status', 'status_display', 'status_class',
            'booking_reference', 'pickup_location', 'dropoff_location', 'special_requests',
            'payment_status', 'payment_method', 'total_price', 'can_cancel', 'refund_amount',
            'is_active', 'cancellation_reason', 'cancelled_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'booking_reference', 'cancellation_reason', 'cancelled_at',
            'created_at', 'updated_at'
        ]

    def get_total_price(self, obj):
        return obj.get_total_price()

    def get_can_cancel(self, obj):
        return obj.can_cancel()

    def get_refund_amount(self, obj):
        return obj.refund_amount

class BookingCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating bookings"""
    
    class Meta:
        model = Booking
        fields = [
            'ride', 'seats', 'pickup_location', 'dropoff_location',
            'special_requests', 'payment_method'
        ]

    def validate_seats(self, value):
        if value < 1 or value > 4:
            raise serializers.ValidationError("Seats must be between 1 and 4.")
        return value

    def validate(self, data):
        ride = data.get('ride')
        seats = data.get('seats', 1)
        request = self.context.get('request')
        
        if not ride:
            raise serializers.ValidationError("Ride is required.")
        
        if not ride.can_book():
            raise serializers.ValidationError("This ride is not available for booking.")
        
        if seats > ride.get_available_seats_count():
            raise serializers.ValidationError(
                f"Only {ride.get_available_seats_count()} seats available."
            )
        
        if request and ride.driver == request.user:
            raise serializers.ValidationError("You cannot book your own ride.")
        
        # Check if user already has a booking for this ride
        if request and Booking.objects.filter(
            ride=ride, passenger=request.user, status__in=['pending', 'confirmed']
        ).exists():
            raise serializers.ValidationError("You already have a booking for this ride.")
        
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['passenger'] = request.user
        return super().create(validated_data)

class RideRequestSerializer(serializers.ModelSerializer):
    """Serializer for ride requests"""
    passenger = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = RideRequest
        fields = [
            'id', 'passenger', 'start_location', 'end_location',
            'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude',
            'preferred_date', 'max_price', 'seats_needed', 'description',
            'is_flexible', 'status', 'created_at', 'expires_at'
        ]
        read_only_fields = ['id', 'passenger', 'created_at', 'expires_at']

    def validate_preferred_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Preferred date must be in the future.")
        return value

    def validate_seats_needed(self, value):
        if value < 1 or value > 4:
            raise serializers.ValidationError("Seats needed must be between 1 and 4.")
        return value

    def validate_max_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Max price must be greater than 0.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['passenger'] = request.user
        return super().create(validated_data)