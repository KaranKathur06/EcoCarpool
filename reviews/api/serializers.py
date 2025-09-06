from rest_framework import serializers
from django.utils import timezone
from ..models import Review, ReviewHelpful, ReviewReport, ReviewTemplate
from users.api.serializers import UserBasicSerializer

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for reviews"""
    reviewer = UserBasicSerializer(read_only=True)
    reviewed = UserBasicSerializer(read_only=True)
    rating_stars = serializers.CharField(source='get_rating_stars', read_only=True)
    aspect_ratings = serializers.SerializerMethodField()
    can_respond = serializers.BooleanField(read_only=True)
    is_helpful = serializers.SerializerMethodField()
    review_type_display = serializers.CharField(source='get_review_type_display', read_only=True)
    
    class Meta:
        model = Review
        fields = [
            'id', 'reviewer', 'reviewed', 'ride', 'booking', 'review_type',
            'review_type_display', 'rating', 'rating_stars', 'comment', 'aspects',
            'aspect_ratings', 'is_anonymous', 'is_public', 'helpful_count',
            'is_verified', 'response', 'response_date', 'can_respond',
            'is_helpful', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'reviewer', 'helpful_count', 'is_verified', 'response_date',
            'created_at', 'updated_at'
        ]

    def get_aspect_ratings(self, obj):
        return obj.get_aspect_ratings()

    def get_is_helpful(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ReviewHelpful.objects.filter(review=obj, user=request.user).exists()
        return False

class ReviewCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating reviews"""
    
    class Meta:
        model = Review
        fields = [
            'reviewed', 'ride', 'booking', 'review_type', 'rating',
            'comment', 'aspects', 'is_anonymous', 'is_public'
        ]

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_comment(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        ride = data.get('ride')
        review_type = data.get('review_type')
        reviewed = data.get('reviewed')
        booking = data.get('booking')

        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Authentication required.")

        # Check if ride is completed
        if ride.status != 'completed':
            raise serializers.ValidationError("You can only review completed rides.")

        # Validate review type permissions
        if review_type == 'driver_to_passenger':
            if ride.driver != request.user:
                raise serializers.ValidationError("Only the driver can review passengers.")
            if booking and booking.passenger != reviewed:
                raise serializers.ValidationError("Invalid passenger for this review.")
        
        elif review_type == 'passenger_to_driver':
            if ride.driver != reviewed:
                raise serializers.ValidationError("You can only review the driver of this ride.")
            if booking and booking.passenger != request.user:
                raise serializers.ValidationError("Only passengers can review the driver.")

        # Check if review already exists
        if Review.objects.filter(
            reviewer=request.user, ride=ride, review_type=review_type
        ).exists():
            raise serializers.ValidationError("You have already reviewed this ride.")

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['reviewer'] = request.user
        return super().create(validated_data)

class ReviewUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating reviews"""
    
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'aspects', 'is_anonymous', 'is_public']

    def validate_rating(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate_comment(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Comment must be at least 10 characters long.")
        return value

class ReviewResponseSerializer(serializers.Serializer):
    """Serializer for adding responses to reviews"""
    response = serializers.CharField(max_length=500, required=True)

    def validate_response(self, value):
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Response must be at least 5 characters long.")
        return value

    def save(self):
        review = self.context['review']
        request = self.context['request']
        
        if review.reviewed != request.user:
            raise serializers.ValidationError("You can only respond to reviews about you.")
        
        if review.response:
            raise serializers.ValidationError("You have already responded to this review.")
        
        review.add_response(self.validated_data['response'])
        return review

class ReviewHelpfulSerializer(serializers.ModelSerializer):
    """Serializer for marking reviews as helpful"""
    
    class Meta:
        model = ReviewHelpful
        fields = ['id', 'review', 'created_at']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        return super().create(validated_data)

class ReviewReportSerializer(serializers.ModelSerializer):
    """Serializer for reporting reviews"""
    reporter = UserBasicSerializer(read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ReviewReport
        fields = [
            'id', 'review', 'reporter', 'reason', 'reason_display',
            'description', 'status', 'status_display', 'admin_notes',
            'resolved_by', 'resolved_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'reporter', 'status', 'admin_notes', 'resolved_by',
            'resolved_at', 'created_at'
        ]

    def validate_description(self, value):
        if len(value.strip()) < 10:
            raise serializers.ValidationError("Description must be at least 10 characters long.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['reporter'] = request.user
        return super().create(validated_data)

class ReviewTemplateSerializer(serializers.ModelSerializer):
    """Serializer for review templates"""
    template_type_display = serializers.CharField(source='get_template_type_display', read_only=True)
    
    class Meta:
        model = ReviewTemplate
        fields = [
            'id', 'title', 'content', 'template_type', 'template_type_display',
            'suggested_rating', 'is_active', 'usage_count', 'created_at'
        ]
        read_only_fields = ['id', 'usage_count', 'created_at']

class ReviewStatsSerializer(serializers.Serializer):
    """Serializer for review statistics"""
    total_reviews = serializers.IntegerField()
    average_rating = serializers.FloatField()
    rating_distribution = serializers.DictField()
    recent_reviews = ReviewSerializer(many=True)
    
    def to_representation(self, instance):
        # instance should be a user object
        from django.db.models import Avg, Count
        
        reviews = Review.objects.filter(reviewed=instance, is_public=True)
        
        # Calculate statistics
        total_reviews = reviews.count()
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        
        # Rating distribution
        rating_dist = reviews.values('rating').annotate(
            count=Count('rating')
        ).order_by('rating')
        rating_distribution = {str(item['rating']): item['count'] for item in rating_dist}
        
        # Recent reviews
        recent_reviews = reviews.order_by('-created_at')[:5]
        
        return {
            'total_reviews': total_reviews,
            'average_rating': round(avg_rating, 2),
            'rating_distribution': rating_distribution,
            'recent_reviews': ReviewSerializer(
                recent_reviews, many=True, context=self.context
            ).data
        }