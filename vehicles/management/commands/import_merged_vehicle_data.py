from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleCompany, VehicleModel
import re
import os

class Command(BaseCommand):
    help = 'Import vehicle types, companies, and models from merged_vehicle_database.sql'

    def handle(self, *args, **options):
        # Look for the SQL file in the project root (same directory as manage.py)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        sql_path = os.path.join(base_dir, 'merged_vehicle_database.sql')
        if not os.path.exists(sql_path):
            self.stdout.write(self.style.ERROR(f'SQL file not found: {sql_path}'))
            return

        with open(sql_path, 'r', encoding='utf-8') as f:
            sql = f.read()

        # Get or create default vehicle type for NULL type_ids
        default_type, _ = VehicleType.objects.get_or_create(
            type_name='Unknown',
            defaults={'description': 'Default type for models with NULL type_id'}
        )

        # Extract vehicle types (car_type)
        type_pattern = re.compile(r"INSERT INTO car_type \(type_name\) VALUES\s*(.*?);", re.DOTALL)
        type_matches = type_pattern.findall(sql)
        type_list = []
        for match in type_matches:
            for t in re.findall(r"'([^']+)'", match):
                type_list.append(t.strip())
        
        # Create type mapping dictionary
        type_mapping = {}
        for idx, t in enumerate(type_list, start=1):
            obj, created = VehicleType.objects.get_or_create(type_name=t)
            type_mapping[str(idx)] = obj  # Map SQL ID to database object
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created new vehicle type: {t}'))
            else:
                self.stdout.write(self.style.WARNING(f'Found existing vehicle type: {t}'))
        self.stdout.write(self.style.SUCCESS(f'Processed {len(type_mapping)} vehicle types.'))

        # Extract companies (car_brand)
        brand_pattern = re.compile(r"INSERT INTO car_brand \(brand_name\) VALUES\s*(.*?);", re.DOTALL)
        brand_matches = brand_pattern.findall(sql)
        brand_list = []
        for match in brand_matches:
            for b in re.findall(r"'([^']+)'", match):
                brand_list.append(b.strip())
        
        # Create brand mapping dictionary
        brand_mapping = {}
        for idx, b in enumerate(brand_list, start=1):
            # First try to get an existing company
            existing_company = VehicleCompany.objects.filter(company_name=b).first()
            if existing_company:
                brand_mapping[str(idx)] = existing_company  # Map SQL ID to database object
                self.stdout.write(self.style.WARNING(f'Using existing company: {b}'))
            else:
                # If no existing company, create a new one
                new_company = VehicleCompany.objects.create(
                    company_name=b,
                    country_of_origin='Unknown'
                )
                brand_mapping[str(idx)] = new_company  # Map SQL ID to database object
                self.stdout.write(self.style.SUCCESS(f'Created new company: {b}'))
        self.stdout.write(self.style.SUCCESS(f'Processed {len(brand_mapping)} companies.'))

        # Extract models (car_model)
        model_pattern = re.compile(r"INSERT INTO car_model \(model_name, brand_id, type_id\) VALUES\s*(.*?);", re.DOTALL)
        model_matches = model_pattern.findall(sql)
        model_count = 0
        skipped_count = 0
        fixed_count = 0
        null_typeid_models = []
        
        for match in model_matches:
            for row in re.findall(r"\(([^)]+)\)", match):
                parts = [p.strip().strip("'") for p in row.split(',')]
                if len(parts) != 3:
                    skipped_count += 1
                    continue
                    
                model_name, brand_id, type_id = parts
                try:
                    # Get brand and type from mapping dictionaries using SQL IDs
                    brand = brand_mapping.get(brand_id)
                    
                    # Handle NULL type_id
                    if type_id.upper() == 'NULL':
                        vtype = default_type
                        fixed_count += 1
                        null_typeid_models.append(f"{model_name} (brand_id: {brand_id})")
                    else:
                        vtype = type_mapping.get(type_id)
                    
                    # If brand not found, try to find it by name in the brand_list
                    if not brand and brand_id.isdigit() and 0 < int(brand_id) <= len(brand_list):
                        brand_name = brand_list[int(brand_id) - 1]
                        brand = VehicleCompany.objects.filter(company_name=brand_name).first()
                        if brand:
                            brand_mapping[brand_id] = brand  # Update mapping for future use
                            fixed_count += 1
                    
                    if not brand:
                        skipped_count += 1
                        self.stdout.write(self.style.WARNING(f'Skipped model {model_name} - brand not found (brand_id: {brand_id})'))
                        continue
                        
                    # Check if model already exists
                    existing_model = VehicleModel.objects.filter(
                        model_name=model_name,
                        company=brand,
                        type=vtype
                    ).first()
                    
                    if existing_model:
                        self.stdout.write(self.style.WARNING(f'Found existing model: {model_name}'))
                    else:
                        VehicleModel.objects.create(
                            model_name=model_name,
                            company=brand,
                            type=vtype,
                            year_from=2020,
                            is_active=True
                        )
                        self.stdout.write(self.style.SUCCESS(f'Created new model: {model_name}'))
                    model_count += 1
                except Exception as e:
                    skipped_count += 1
                    self.stdout.write(self.style.ERROR(f'Error processing model {model_name}: {str(e)}'))
                    continue

        self.stdout.write(self.style.SUCCESS(f'Successfully imported {model_count} vehicle models.'))
        if fixed_count > 0:
            self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} models with NULL type_ids or missing brand references.'))
        if skipped_count > 0:
            self.stdout.write(self.style.WARNING(f'Skipped {skipped_count} models due to errors or missing references.'))
        self.stdout.write(self.style.SUCCESS('Vehicle data import complete.'))

        # Write out models with NULL type_id
        if null_typeid_models:
            null_typeid_path = os.path.join(base_dir, 'null_typeid_models.txt')
            with open(null_typeid_path, 'w', encoding='utf-8') as f:
                for entry in null_typeid_models:
                    f.write(entry + '\n')
            self.stdout.write(self.style.WARNING(f'List of models with NULL type_id written to {null_typeid_path}')) 