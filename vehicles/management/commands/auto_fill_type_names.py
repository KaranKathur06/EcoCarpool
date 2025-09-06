from django.core.management.base import BaseCommand
import csv
import os

# Heuristic mapping: keyword (lowercase) -> type_name
KEYWORD_TYPE_MAP = {
    'suv': 'SUV',
    'sedan': 'Sedan',
    'hatchback': 'Hatchback',
    'coupe': 'Coupe',
    'convertible': 'Convertible',
    'truck': 'Truck',
    'electric': 'Electric',
    'ev': 'Electric',
    'hybrid': 'Hybrid',
    'van': 'Van',
    'wagon': 'Wagon',
    'pickup': 'Pickup',
    'roadster': 'Roadster',
    'crossover': 'Crossover',
    'minivan': 'Minivan',
    'sport': 'Coupe',
    'luxury': 'Sedan',
    'touring': 'Sedan',
    'compact': 'Hatchback',
    'saloon': 'Sedan',
}

class Command(BaseCommand):
    help = "Auto-fill type_name in model_type_mapping.csv using heuristics."

    def handle(self, *args, **options):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        csv_path = os.path.join(base_dir, 'model_type_mapping.csv')
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
            return

        # Read all rows
        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))
            fieldnames = reader[0].keys() if reader else ['model_name', 'brand_name', 'type_name']

        filled = 0
        for row in reader:
            if row['type_name'].strip():
                continue  # Already filled
            model = row['model_name'].lower()
            brand = row['brand_name'].lower()
            found = False
            for keyword, type_name in KEYWORD_TYPE_MAP.items():
                if keyword in model or keyword in brand:
                    row['type_name'] = type_name
                    filled += 1
                    found = True
                    break
            if not found:
                row['type_name'] = ''  # Explicitly blank if not found

        # Write back to CSV
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in reader:
                writer.writerow(row)

        self.stdout.write(self.style.SUCCESS(f'Auto-filled {filled} type_name values in {csv_path}')) 