from rest_framework import serializers
from ..models import Vehicle, VehicleType, VehicleCompany, VehicleModel, VehicleDocument, VehicleMaintenanceRecord

class VehicleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleType
        fields = ['id', 'type_name', 'description', 'category', 'is_popular']

class VehicleCompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = VehicleCompany
        fields = ['id', 'company_name', 'is_luxury', 'country_of_origin', 'parent_company', 'is_active']

class VehicleModelSerializer(serializers.ModelSerializer):
    company = VehicleCompanySerializer(read_only=True)
    type = VehicleTypeSerializer(read_only=True)
    
    class Meta:
        model = VehicleModel
        fields = [
            'id', 'model_name', 'company', 'type', 'year_from', 'year_to',
            'base_price', 'is_active', 'drive_type', 'body_style'
        ]

class VehicleBasicSerializer(serializers.ModelSerializer):
    """Basic vehicle serializer for nested use"""
    company_name = serializers.CharField(source='company.company_name', read_only=True)
    model_name = serializers.CharField(source='model.model_name', read_only=True)
    fuel_efficiency = serializers.CharField(source='get_fuel_efficiency_display', read_only=True)
    condition_class = serializers.CharField(source='get_condition_badge_class', read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'company_name', 'model_name', 'license_plate', 'color',
            'year', 'seating_capacity', 'fuel_type', 'fuel_efficiency',
            'condition', 'condition_class', 'vehicle_photo', 'is_verified'
        ]

class VehicleListSerializer(serializers.ModelSerializer):
    """Serializer for vehicle list view"""
    owner = serializers.StringRelatedField(read_only=True)
    company = VehicleCompanySerializer(read_only=True)
    model = VehicleModelSerializer(read_only=True)
    vehicle_type = VehicleTypeSerializer(read_only=True)
    fuel_efficiency = serializers.CharField(source='get_fuel_efficiency_display', read_only=True)
    condition_class = serializers.CharField(source='get_condition_badge_class', read_only=True)
    is_documents_valid = serializers.BooleanField(read_only=True)
    needs_service = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'vehicle_type', 'company', 'model', 'license_plate',
            'color', 'year', 'seating_capacity', 'fuel_type', 'fuel_efficiency',
            'condition', 'condition_class', 'vehicle_photo', 'is_verified',
            'is_active', 'is_available_for_rides', 'is_documents_valid',
            'needs_service', 'created_at'
        ]

class VehicleDetailSerializer(serializers.ModelSerializer):
    """Detailed vehicle serializer"""
    owner = serializers.StringRelatedField(read_only=True)
    company = VehicleCompanySerializer(read_only=True)
    model = VehicleModelSerializer(read_only=True)
    vehicle_type = VehicleTypeSerializer(read_only=True)
    documents = serializers.SerializerMethodField()
    maintenance_records = serializers.SerializerMethodField()
    fuel_efficiency = serializers.CharField(source='get_fuel_efficiency_display', read_only=True)
    condition_class = serializers.CharField(source='get_condition_badge_class', read_only=True)
    is_documents_valid = serializers.BooleanField(read_only=True)
    needs_service = serializers.BooleanField(read_only=True)
    total_rides = serializers.SerializerMethodField()
    total_earnings = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = [
            'id', 'owner', 'vehicle_type', 'company', 'model', 'license_plate',
            'color', 'year', 'seating_capacity', 'fuel_type', 'mileage',
            'fuel_efficiency', 'odometer_reading', 'condition', 'condition_class',
            'vehicle_photo', 'additional_photos', 'features', 'description',
            'is_verified', 'is_active', 'is_available_for_rides',
            'insurance_expiry', 'registration_expiry', 'pollution_certificate_expiry',
            'last_service_date', 'next_service_due', 'is_documents_valid',
            'needs_service', 'total_rides', 'total_earnings', 'average_rating',
            'documents', 'maintenance_records', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']

    def get_documents(self, obj):
        documents = obj.documents.filter(is_active=True)
        return VehicleDocumentSerializer(documents, many=True, context=self.context).data

    def get_maintenance_records(self, obj):
        records = obj.maintenance_records.all()[:5]  # Latest 5 records
        return VehicleMaintenanceRecordSerializer(records, many=True).data

    def get_total_rides(self, obj):
        return obj.get_total_rides()

    def get_total_earnings(self, obj):
        return obj.get_total_earnings()

    def get_average_rating(self, obj):
        return obj.get_average_rating()

class VehicleCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating vehicles"""
    
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type', 'company', 'model', 'license_plate', 'color',
            'year', 'seating_capacity', 'fuel_type', 'mileage', 'odometer_reading',
            'condition', 'vehicle_photo', 'features', 'description',
            'is_available_for_rides', 'insurance_expiry', 'registration_expiry',
            'pollution_certificate_expiry', 'last_service_date', 'next_service_due'
        ]

    def validate_year(self, value):
        from django.utils import timezone
        current_year = timezone.now().year
        if value < 1990 or value > current_year + 1:
            raise serializers.ValidationError(f"Year must be between 1990 and {current_year + 1}.")
        return value

    def validate_seating_capacity(self, value):
        if value < 2 or value > 10:
            raise serializers.ValidationError("Seating capacity must be between 2 and 10.")
        return value

    def validate_license_plate(self, value):
        # Check if license plate already exists for another vehicle
        if self.instance:
            if Vehicle.objects.filter(license_plate=value).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError("A vehicle with this license plate already exists.")
        else:
            if Vehicle.objects.filter(license_plate=value).exists():
                raise serializers.ValidationError("A vehicle with this license plate already exists.")
        return value.upper()

    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['owner'] = request.user
        return super().create(validated_data)

class VehicleDocumentSerializer(serializers.ModelSerializer):
    """Serializer for vehicle documents"""
    status_class = serializers.CharField(source='get_status_badge_class', read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    days_until_expiry = serializers.IntegerField(read_only=True)
    is_expiring_soon = serializers.BooleanField(read_only=True)
    document_type_display = serializers.CharField(source='get_document_type_display', read_only=True)
    
    class Meta:
        model = VehicleDocument
        fields = [
            'id', 'document_type', 'document_type_display', 'document_number',
            'issue_date', 'expiry_date', 'document_file', 'status', 'status_class',
            'verified_by', 'verified_at', 'rejection_reason', 'notes',
            'is_expired', 'days_until_expiry', 'is_expiring_soon',
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'status', 'verified_by', 'verified_at', 'rejection_reason',
            'created_at', 'updated_at'
        ]

class VehicleMaintenanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for vehicle maintenance records"""
    maintenance_type_display = serializers.CharField(source='get_maintenance_type_display', read_only=True)
    
    class Meta:
        model = VehicleMaintenanceRecord
        fields = [
            'id', 'maintenance_type', 'maintenance_type_display', 'description',
            'cost', 'service_provider', 'odometer_reading', 'service_date',
            'next_service_due', 'receipt_file', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

    def validate_service_date(self, value):
        from django.utils import timezone
        if value > timezone.now().date():
            raise serializers.ValidationError("Service date cannot be in the future.")
        return value

    def validate_cost(self, value):
        if value < 0:
            raise serializers.ValidationError("Cost cannot be negative.")
        return value

    def create(self, validated_data):
        # Get vehicle from context or URL
        vehicle_id = self.context.get('vehicle_id')
        if vehicle_id:
            validated_data['vehicle_id'] = vehicle_id
        return super().create(validated_data)