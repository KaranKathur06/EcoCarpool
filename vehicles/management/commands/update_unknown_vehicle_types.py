from django.core.management.base import BaseCommand
from vehicles.models import VehicleModel, VehicleType, VehicleCompany
import csv
import os

class Command(BaseCommand):
    help = 'Update VehicleModels with Unknown type to the correct type using a CSV mapping'

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_path = os.path.join(base_dir, 'model_type_mapping.csv')
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            updated = 0
            for row in reader:
                model_name = row['model_name'].strip()
                brand_name = row['brand_name'].strip()
                type_name = row['type_name'].strip()
                try:
                    vtype = VehicleType.objects.get(type_name__iexact=type_name)
                    brand = VehicleCompany.objects.get(company_name__iexact=brand_name)
                    models = VehicleModel.objects.filter(model_name__iexact=model_name, company=brand, type__type_name='Unknown')
                    for model in models:
                        model.type = vtype
                        model.save()
                        updated += 1
                        self.stdout.write(self.style.SUCCESS(f'Updated {model_name} ({brand_name}) to type {type_name}'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error updating {model_name} ({brand_name}): {e}'))
            self.stdout.write(self.style.SUCCESS(f'Updated {updated} models.')) 