from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleModel
from django.db import transaction

class Command(BaseCommand):
    help = 'Simplify vehicle types to basic, user-friendly categories'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Define basic vehicle types that most people understand
            basic_types = {
                'Sedan': 'A standard 4-door car, good for families and everyday use',
                'SUV': 'Spacious vehicle with higher ground clearance',
                'Hatchback': 'Compact car with rear door that opens upwards',
                'Electric Car': 'Environment-friendly vehicle running on electricity',
                'Minivan': 'Large family vehicle with sliding doors',
                'Pickup Truck': 'Vehicle with an open cargo area in the back',
                'Luxury Car': 'Premium vehicle with high-end features',
                'Sports Car': 'High-performance vehicle with sporty design'
            }

            # First, create new basic types
            self.stdout.write('Creating basic vehicle types...')
            type_mapping = {}
            
            for type_name, description in basic_types.items():
                vehicle_type, created = VehicleType.objects.get_or_create(
                    name=type_name,
                    defaults={'description': description}
                )
                type_mapping[type_name] = vehicle_type
                if created:
                    self.stdout.write(f'Created vehicle type: {type_name}')
                else:
                    self.stdout.write(f'Using existing vehicle type: {type_name}')

            # Map existing types to basic types
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
                'MPV': 'Minivan',
                'Pickup': 'Pickup Truck',
                'Jeep': 'SUV',
                'Part-time 4-Wheel Drive': 'SUV'
            }

            # Update all vehicle models to use the new basic types
            self.stdout.write('Updating vehicle models with simplified types...')
            
            for old_type_name, new_type_name in mapping_rules.items():
                models = VehicleModel.objects.filter(vehicle_type__name=old_type_name)
                if models.exists():
                    models.update(vehicle_type=type_mapping[new_type_name])
                    self.stdout.write(f'Updated {models.count()} models from {old_type_name} to {new_type_name}')

            # Delete old unused vehicle types
            VehicleType.objects.exclude(name__in=basic_types.keys()).delete()

            self.stdout.write(self.style.SUCCESS('Successfully simplified vehicle types')) 