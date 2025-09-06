from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from ..models import CustomUser

class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for nested use"""
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'profile_picture', 'avatar_url', 'role'
        ]
        read_only_fields = ['id', 'username']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_avatar_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

class UserProfileSerializer(serializers.ModelSerializer):
    """Detailed user profile serializer"""
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    total_rides_as_driver = serializers.SerializerMethodField()
    total_rides_as_passenger = serializers.SerializerMethodField()
    total_earnings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    co2_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'role', 'bio', 'address', 'phone_number', 'profile_picture', 'avatar_url',
            'is_active', 'is_verified', 'date_joined',
            'total_rides_as_driver', 'total_rides_as_passenger', 'total_earnings',
            'average_rating', 'co2_saved'
        ]
        read_only_fields = [
            'id', 'username', 'is_active', 'is_verified', 'date_joined',
            'total_rides_as_driver', 'total_rides_as_passenger', 'total_earnings',
            'average_rating', 'co2_saved'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_avatar_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def get_total_rides_as_driver(self, obj):
        return obj.driver_rides.filter(status='completed').count()

    def get_total_rides_as_passenger(self, obj):
        return obj.bookings.filter(status='completed').count()

    def get_total_earnings(self, obj):
        return obj.get_total_earnings()

    def get_average_rating(self, obj):
        return obj.get_average_rating()

    def get_co2_saved(self, obj):
        return obj.get_co2_saved()

class UserSerializer(serializers.ModelSerializer):
    """Complete user serializer for API responses"""
    full_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    stats = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'phone_number', 'date_of_birth', 'gender', 'profile_picture', 
            'avatar_url', 'bio', 'role', 'is_verified', 'rating', 'stats',
            'date_joined', 'last_login'
        ]
        read_only_fields = [
            'id', 'username', 'is_verified', 'rating', 'date_joined', 'last_login'
        ]

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    def get_avatar_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None

    def get_stats(self, obj):
        return {
            'total_rides': getattr(obj, 'total_rides', 0),
            'total_bookings': getattr(obj, 'total_bookings', 0),
            'total_earnings': float(getattr(obj, 'total_earnings', 0)),
            'rating': float(obj.rating or 0),
            'reviews_count': getattr(obj, 'reviews_count', 0)
        }

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'phone_number', 'password', 'confirm_password'
        ]

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value

    def validate(self, data):
        if data['password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match.")
        data.pop('confirm_password')
        return data

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile"""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'bio', 'address', 
            'phone_number', 'profile_picture'
        ]

    def validate_phone_number(self, value):
        if value and CustomUser.objects.filter(
            phone_number=value
        ).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError("This phone number is already in use.")
        return value

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match.")
        return data

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user

class UserStatsSerializer(serializers.ModelSerializer):
    """Serializer for user statistics"""
    total_rides_as_driver = serializers.SerializerMethodField()
    total_rides_as_passenger = serializers.SerializerMethodField()
    total_earnings = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    average_rating_as_driver = serializers.SerializerMethodField()
    average_rating_as_passenger = serializers.SerializerMethodField()
    co2_saved = serializers.SerializerMethodField()
    fuel_saved = serializers.SerializerMethodField()
    total_distance = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomUser
        fields = [
            'total_rides_as_driver', 'total_rides_as_passenger',
            'total_earnings', 'total_spent', 'average_rating_as_driver',
            'average_rating_as_passenger', 'co2_saved', 'fuel_saved',
            'total_distance'
        ]

    def get_total_rides_as_driver(self, obj):
        return obj.driver_rides.filter(status='completed').count()

    def get_total_rides_as_passenger(self, obj):
        return obj.bookings.filter(status='completed').count()

    def get_total_earnings(self, obj):
        return obj.get_total_earnings()

    def get_total_spent(self, obj):
        from django.db.models import Sum, F
        return obj.bookings.filter(
            status='completed'
        ).aggregate(
            total=Sum(F('seats') * F('ride__price_per_seat'))
        )['total'] or 0

    def get_average_rating_as_driver(self, obj):
        from django.db.models import Avg
        return obj.driver_rides.filter(
            reviews__isnull=False
        ).aggregate(
            avg_rating=Avg('reviews__rating')
        )['avg_rating'] or 0

    def get_average_rating_as_passenger(self, obj):
        from django.db.models import Avg
        return obj.passenger_reviews.aggregate(
            avg_rating=Avg('rating')
        )['avg_rating'] or 0

    def get_co2_saved(self, obj):
        return obj.get_co2_saved()

    def get_fuel_saved(self, obj):
        return obj.get_fuel_saved()

    def get_total_distance(self, obj):
        from django.db.models import Sum
        driver_distance = obj.driver_rides.filter(
            status='completed'
        ).aggregate(
            total=Sum('distance')
        )['total'] or 0
        
        passenger_distance = obj.bookings.filter(
            status='completed'
        ).aggregate(
            total=Sum('ride__distance')
        )['total'] or 0
        
        return driver_distance + passenger_distance