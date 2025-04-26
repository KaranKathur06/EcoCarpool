from django.contrib import admin
from .models import VehicleType, VehicleCompany, VehicleModel, Vehicle, VehicleDocument

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'description')
    search_fields = ('type_name',)

@admin.register(VehicleCompany)
class VehicleCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'country_of_origin', 'is_luxury')
    list_filter = ('country_of_origin', 'is_luxury')
    search_fields = ('company_name',)

@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'company', 'type', 'year_from', 'year_to', 'base_price', 'is_active')
    list_filter = ('company', 'type', 'is_active')
    search_fields = ('model_name', 'company__company_name')
    list_editable = ('is_active',)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'company', 'model', 'color', 'year', 'is_active')
    list_filter = ('vehicle_type', 'company', 'fuel_type', 'is_active')
    search_fields = ('license_plate', 'owner__username', 'company__company_name', 'model__model_name')
    list_editable = ('is_active',)

@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'document_type', 'expiry_date', 'is_verified', 'uploaded_at')
    list_filter = ('document_type', 'is_verified')
    search_fields = ('vehicle__license_plate',)
    list_editable = ('is_verified',)