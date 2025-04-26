from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleCompany

class Command(BaseCommand):
    help = 'Sets up initial vehicle types and companies'

    def handle(self, *args, **kwargs):
        # Clear existing data
        VehicleType.objects.all().delete()
        VehicleCompany.objects.all().delete()

        # Create vehicle types
        vehicle_types = [
            ('Sedan', 'A four-door passenger car with a trunk'),
            ('SUV', 'Sport Utility Vehicle with high ground clearance'),
            ('Hatchback', 'A car with a rear door that opens upwards'),
            ('Luxury', 'High-end premium vehicles')
        ]
        for type_name, description in vehicle_types:
            VehicleType.objects.create(type_name=type_name, description=description)
            self.stdout.write(self.style.SUCCESS(f'Created vehicle type: {type_name}'))

        # Create vehicle companies
        companies = [
            ('Toyota', False, 'Japan'),
            ('Honda', False, 'Japan'),
            ('BMW', True, 'Germany'),
            ('Mercedes-Benz', True, 'Germany')
        ]
        for name, is_luxury, country in companies:
            VehicleCompany.objects.create(
                company_name=name,
                is_luxury=is_luxury,
                country_of_origin=country
            )
            self.stdout.write(self.style.SUCCESS(f'Created company: {name}'))

        self.stdout.write(self.style.SUCCESS('Successfully set up vehicle data')) 