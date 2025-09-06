from django.core.management.base import BaseCommand
from vehicles.models import VehicleType
import csv
import os

class Command(BaseCommand):
    help = "Add missing VehicleType entries from model_type_mapping.csv."

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_path = os.path.join(base_dir, 'model_type_mapping.csv')
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            type_names = set(row['type_name'].strip() for row in reader if row['type_name'].strip())
        added = 0
        for type_name in type_names:
            obj, created = VehicleType.objects.get_or_create(type_name=type_name, defaults={"description": f"Auto-added from CSV"})
            if created:
                self.stdout.write(self.style.SUCCESS(f'Added VehicleType: {type_name}'))
                added += 1
        self.stdout.write(self.style.SUCCESS(f'Added {added} new VehicleType entries.')) 