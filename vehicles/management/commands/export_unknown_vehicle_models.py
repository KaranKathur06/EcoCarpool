from django.core.management.base import BaseCommand
from vehicles.models import VehicleModel
import csv
import os

class Command(BaseCommand):
    help = "Export all VehicleModels with type 'Unknown' to a CSV for manual type assignment."

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_path = os.path.join(base_dir, 'model_type_mapping.csv')
        models = VehicleModel.objects.filter(type__type_name='Unknown')
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['model_name', 'brand_name', 'type_name'])
            for m in models:
                writer.writerow([m.model_name, m.company.company_name, ''])
        self.stdout.write(self.style.SUCCESS(f'Exported {models.count()} models to {csv_path}')) 