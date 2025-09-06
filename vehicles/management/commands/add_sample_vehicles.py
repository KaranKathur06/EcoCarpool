from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleCompany, VehicleModel

class Command(BaseCommand):
    help = 'Adds sample vehicle data'

    def handle(self, *args, **kwargs):
        # Create Vehicle Types
        vehicle_types = {
            'Sedan': 'A standard 4-door car, good for families and everyday use',
            'SUV': 'Spacious vehicle with higher ground clearance',
            'Hatchback': 'Compact car with rear door that opens upwards',
            'Electric Car': 'Environment-friendly vehicle running on electricity',
            'Minivan': 'Large family vehicle with sliding doors',
            'Pickup Truck': 'Vehicle with an open cargo area in the back',
            'Luxury Car': 'High-end luxury vehicles with premium features',
            'Sports Car': 'High-performance vehicle with sporty design',
            'Crossover': 'Combines features of an SUV with a passenger car',
            'MPV': 'Multi-Purpose Vehicle designed to transport passengers'
        }

        type_objects = {}
        for type_name, description in vehicle_types.items():
            vehicle_type, created = VehicleType.objects.get_or_create(
                name=type_name,
                defaults={'description': description}
            )
            type_objects[type_name] = vehicle_type
            if created:
                self.stdout.write(f'Created vehicle type: {type_name}')
            else:
                self.stdout.write(f'Using existing vehicle type: {type_name}')

        # Create Companies
        companies = {
            'Toyota': 'Japan',
            'Honda': 'Japan',
            'BMW': 'Germany',
            'Mercedes-Benz': 'Germany',
            'Audi': 'Germany',
            'Tesla': 'USA',
            'Ford': 'USA',
            'Hyundai': 'South Korea',
            'Kia': 'South Korea',
            'Volkswagen': 'Germany',
            'Maruti Suzuki': 'India',
            'Mahindra': 'India'
        }

        company_objects = {}
        for name, country in companies.items():
            company, created = VehicleCompany.objects.get_or_create(
                company_name=name,
                defaults={
                    'country_of_origin': country,
                    'is_luxury': False
                }
            )
            company_objects[name] = company
            if created:
                self.stdout.write(f'Created company: {name}')
            else:
                self.stdout.write(f'Using existing company: {name}')

        # Create Models
        models_data = [
            # Toyota Models
            ('Camry', 'Toyota', 'Sedan', 2020),
            ('Fortuner', 'Toyota', 'SUV', 2020),
            ('Innova', 'Toyota', 'MPV', 2020),
            ('Corolla', 'Toyota', 'Sedan', 2020),
            ('RAV4', 'Toyota', 'Crossover', 2020),
            
            # Honda Models
            ('Civic', 'Honda', 'Sedan', 2020),
            ('CR-V', 'Honda', 'SUV', 2020),
            ('City', 'Honda', 'Sedan', 2020),
            ('Jazz', 'Honda', 'Hatchback', 2020),
            
            # BMW Models
            ('3 Series', 'BMW', 'Sedan', 2020),
            ('X5', 'BMW', 'SUV', 2020),
            ('M3', 'BMW', 'Sports Car', 2020),
            ('7 Series', 'BMW', 'Luxury Car', 2020),
            
            # Mercedes Models
            ('C-Class', 'Mercedes-Benz', 'Sedan', 2020),
            ('GLC', 'Mercedes-Benz', 'SUV', 2020),
            ('S-Class', 'Mercedes-Benz', 'Luxury Car', 2020),
            ('AMG GT', 'Mercedes-Benz', 'Sports Car', 2020),
            
            # Audi Models
            ('A4', 'Audi', 'Sedan', 2020),
            ('Q5', 'Audi', 'SUV', 2020),
            ('RS', 'Audi', 'Sports Car', 2020),
            ('A8', 'Audi', 'Luxury Car', 2020),
            
            # Tesla Models
            ('Model 3', 'Tesla', 'Electric Car', 2020),
            ('Model S', 'Tesla', 'Electric Car', 2020),
            ('Model X', 'Tesla', 'SUV', 2020),
            
            # Ford Models
            ('F-150', 'Ford', 'Pickup Truck', 2020),
            ('Explorer', 'Ford', 'SUV', 2020),
            ('Mustang', 'Ford', 'Sports Car', 2020),
            
            # Hyundai Models
            ('Elantra', 'Hyundai', 'Sedan', 2020),
            ('Tucson', 'Hyundai', 'SUV', 2020),
            ('i20', 'Hyundai', 'Hatchback', 2020),
            
            # Kia Models
            ('Seltos', 'Kia', 'SUV', 2020),
            ('Carnival', 'Kia', 'MPV', 2020),
            ('Rio', 'Kia', 'Hatchback', 2020),
            
            # Volkswagen Models
            ('Golf', 'Volkswagen', 'Hatchback', 2020),
            ('Tiguan', 'Volkswagen', 'SUV', 2020),
            ('Passat', 'Volkswagen', 'Sedan', 2020),
            
            # Maruti Suzuki Models
            ('Swift', 'Maruti Suzuki', 'Hatchback', 2020),
            ('Ertiga', 'Maruti Suzuki', 'MPV', 2020),
            ('Baleno', 'Maruti Suzuki', 'Hatchback', 2020),
            
            # Mahindra Models
            ('Scorpio', 'Mahindra', 'SUV', 2020),
            ('Thar', 'Mahindra', 'SUV', 2020),
            ('XUV700', 'Mahindra', 'SUV', 2020)
        ]

        # First, deactivate all existing models
        VehicleModel.objects.all().update(is_active=False)

        # Then create or update the new models
        for model_name, company_name, type_name, year_from in models_data:
            model, created = VehicleModel.objects.update_or_create(
                model_name=model_name,
                company=company_objects[company_name],
                defaults={
                    'type': type_objects[type_name],
                    'year_from': year_from,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'Created model: {model_name}')
            else:
                self.stdout.write(f'Updated model: {model_name}')

        self.stdout.write(self.style.SUCCESS('Successfully added sample vehicle data')) 