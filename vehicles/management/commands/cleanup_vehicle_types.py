from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleModel
from django.db import transaction

class Command(BaseCommand):
    help = 'Clean up and standardize vehicle types'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Define standard vehicle types
            standard_types = {
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

            # First, delete all existing vehicle types
            self.stdout.write('Deleting existing vehicle types...')
            VehicleType.objects.all().delete()

            # Create new standard types
            self.stdout.write('Creating standard vehicle types...')
            type_mapping = {}
            
            for type_name, description in standard_types.items():
                vehicle_type = VehicleType.objects.create(
                    name=type_name,
                    description=description
                )
                type_mapping[type_name] = vehicle_type
                self.stdout.write(f'Created vehicle type: {type_name}')

            # Map old types to new types
            mapping_rules = {
                '2-Wheel Drive': 'Sedan',
                '4-Wheel Drive': 'SUV',
                '4-Wheel or All-Wheel Drive': 'SUV',
                'All-Wheel Drive': 'SUV',
                'Front-Wheel Drive': 'Sedan',
                'Rear-Wheel Drive': 'Sedan',
                'Electric vehicle': 'Electric Car',
                'Convertible': 'Sports Car',
                'Coupe': 'Sports Car',
                'Minivan': 'Minivan',
                'MPV': 'MPV',
                'Pickup': 'Pickup Truck',
                'Jeep': 'SUV',
                'Part-time 4-Wheel Drive': 'SUV',
                'Crossover': 'Crossover'
            }

            # Update all vehicle models to use the new types
            self.stdout.write('Updating vehicle models with new types...')
            
            for old_type_name, new_type_name in mapping_rules.items():
                models = VehicleModel.objects.filter(vehicle_type__name=old_type_name)
                if models.exists():
                    models.update(vehicle_type=type_mapping[new_type_name])
                    self.stdout.write(f'Updated {models.count()} models from {old_type_name} to {new_type_name}')

            self.stdout.write(self.style.SUCCESS('Successfully cleaned up vehicle types')) 