from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleCompany, VehicleModel
import sqlite3
import os

class Command(BaseCommand):
    help = 'Import vehicle data from SQL file'

    def handle(self, *args, **options):
        # First, clear existing data
        VehicleModel.objects.all().delete()
        VehicleCompany.objects.all().delete()
        VehicleType.objects.all().delete()

        # Create default vehicle types
        vehicle_types = {
            'Sedan': 'A passenger car with a separate trunk for luggage',
            'SUV': 'Sport Utility Vehicle - larger vehicle with higher ground clearance',
            'Hatchback': 'A car with a rear door that opens upwards',
            'Luxury': 'Premium vehicles with high-end features',
            'Pickup': 'Vehicle with an open cargo area',
            'Van': 'Large vehicle for transporting cargo or passengers',
            'Coupe': 'Two-door car with a fixed roof',
            'Convertible': 'Car with a retractable roof'
        }

        type_objects = {}
        for type_name, description in vehicle_types.items():
            type_obj = VehicleType.objects.create(
                type_name=type_name,
                description=description
            )
            type_objects[type_name] = type_obj
            self.stdout.write(f'Created vehicle type: {type_name}')

        # Import car brands as companies
        with open('merged_vehicle_database.sql', 'r') as f:
            content = f.read()
            # Extract brand names from SQL content
            brands_start = content.find("INSERT INTO car_brand (brand_name) VALUES")
            brands_end = content.find("INSERT INTO car_type")
            brands_section = content[brands_start:brands_end]
            
            # Parse brand names
            brands = []
            for line in brands_section.split('\n'):
                if line.strip().startswith("('") and line.strip().endswith("'),"):
                    brand_name = line.strip()[2:-3]
                    brands.append(brand_name)

            # Create company objects
            for brand_name in brands:
                company = VehicleCompany.objects.create(
                    company_name=brand_name,
                    country_of_origin='Unknown',  # You might want to add this data later
                    is_luxury=brand_name in ['Mercedes-Benz', 'BMW', 'Audi', 'Lexus', 'Porsche', 'Ferrari', 'Lamborghini']
                )
                self.stdout.write(f'Created company: {brand_name}')

        self.stdout.write(self.style.SUCCESS('Successfully imported vehicle data')) 