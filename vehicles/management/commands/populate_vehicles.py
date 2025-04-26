from django.core.management.base import BaseCommand
from vehicles.models import VehicleBrand, VehicleModel

class Command(BaseCommand):
    help = 'Populates vehicle brands and models'

    def handle(self, *args, **kwargs):
        # Car brands and models
        car_brands = {
            'Toyota': ['Corolla', 'Camry', 'RAV4', 'Innova'],
            'Honda': ['City', 'Civic', 'Accord', 'CR-V'],
            'Maruti Suzuki': ['Swift', 'Baleno', 'Dzire', 'Ertiga'],
            'Hyundai': ['i20', 'Verna', 'Creta', 'Venue'],
            'Tata': ['Nexon', 'Harrier', 'Safari', 'Tiago'],
            'Mahindra': ['XUV700', 'Scorpio', 'Thar', 'XUV300'],
            'Kia': ['Seltos', 'Sonet', 'Carens', 'Carnival'],
            'Volkswagen': ['Polo', 'Vento', 'Tiguan', 'Taigun'],
            'Skoda': ['Rapid', 'Kushaq', 'Slavia', 'Octavia'],
            'Renault': ['Kwid', 'Triber', 'Kiger', 'Duster']
        }

        # First clear existing data
        VehicleModel.objects.all().delete()
        VehicleBrand.objects.all().delete()

        # Create car brands and models
        for brand_name, models in car_brands.items():
            brand = VehicleBrand.objects.create(
                name=brand_name,
                vehicle_type='CAR',
                is_active=True
            )
            for model_name in models:
                VehicleModel.objects.create(
                    name=model_name,
                    brand=brand,
                    is_active=True
                )

        self.stdout.write(self.style.SUCCESS('Successfully populated vehicle brands and models')) 