from django.contrib import admin
from .models import Vehicle, VehicleDocument, VehicleType, VehicleCompany, VehicleModel

@admin.register(VehicleType)
class VehicleTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'category', 'is_popular')
    list_filter = ('category', 'is_popular')
    search_fields = ('type_name', 'description')
    ordering = ('category', 'type_name')

@admin.register(VehicleCompany)
class VehicleCompanyAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'is_luxury', 'country_of_origin', 'parent_company', 'is_active')
    list_filter = ('is_luxury', 'country_of_origin', 'is_active')
    search_fields = ('company_name', 'parent_company')
    ordering = ('company_name',)

@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    list_display = ('model_name', 'company', 'type', 'year_from', 'year_to', 'is_active')
    list_filter = ('type', 'company', 'is_active', 'drive_type', 'body_style')
    search_fields = ('model_name', 'company__company_name')
    ordering = ('company__company_name', 'model_name')

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('license_plate', 'owner', 'company', 'model', 'year', 'fuel_type', 'is_active')
    list_filter = ('vehicle_type', 'company', 'fuel_type', 'is_active')
    search_fields = ('license_plate', 'owner__username', 'company__company_name', 'model__model_name')
    ordering = ('-created_at',)

@admin.register(VehicleDocument)
class VehicleDocumentAdmin(admin.ModelAdmin):
    list_display = ('vehicle', 'document_type', 'document_number', 'issue_date', 'expiry_date', 'is_active')
    list_filter = ('document_type', 'is_active')
    search_fields = ('vehicle__license_plate', 'document_number')
    ordering = ('-created_at',)