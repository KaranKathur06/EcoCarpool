from django.core.management.base import BaseCommand
import pandas as pd
from vehicles.models import VehicleType, VehicleCompany, VehicleModel
from django.db import transaction

class Command(BaseCommand):
    help = 'Import new vehicle data from Excel file'

    def add_arguments(self, parser):
        parser.add_argument('excel_file', type=str, help='Path to the Excel file')

    def handle(self, *args, **options):
        excel_file = options['excel_file']
        self.stdout.write(f'Reading data from {excel_file}...')

        # Read the Excel file
        df = pd.read_excel(excel_file)
        
        with transaction.atomic():
            # Process vehicle types (Drive types in the Excel file)
            self.stdout.write('Processing vehicle types...')
            drive_types = df['Drive'].unique()
            type_map = {}
            
            for drive_type in drive_types:
                if pd.notna(drive_type) and drive_type.strip():
                    vehicle_type, created = VehicleType.objects.get_or_create(
                        name=drive_type.strip(),
                        defaults={'description': f'Vehicle with {drive_type} drive system'}
                    )
                    type_map[drive_type] = vehicle_type
                    if created:
                        self.stdout.write(f'Created vehicle type: {drive_type}')
                    else:
                        self.stdout.write(f'Using existing vehicle type: {drive_type}')

            # Process companies/brands (Make in the Excel file)
            self.stdout.write('Processing vehicle companies...')
            makes = df['Make'].unique()
            company_map = {}
            
            for make in makes:
                if pd.notna(make) and make.strip():
                    company, created = VehicleCompany.objects.get_or_create(
                        name=make.strip(),
                        defaults={
                            'country': 'Unknown',  # Default value
                            'website': f'https://www.{make.lower().replace(" ", "")}.com'  # Default website
                        }
                    )
                    company_map[make] = company
                    if created:
                        self.stdout.write(f'Created vehicle company: {make}')
                    else:
                        self.stdout.write(f'Using existing company: {make}')

            # Process vehicle models
            self.stdout.write('Processing vehicle models...')
            processed_models = set()
            
            for _, row in df.iterrows():
                make = row['Make']
                model = row['Model']
                drive = row['Drive']
                year = row['Year']
                
                if pd.notna(make) and pd.notna(model) and pd.notna(drive) and pd.notna(year):
                    make = make.strip()
                    model = model.strip()
                    drive = drive.strip()
                    
                    # Create a unique identifier for the model
                    model_key = f"{make}_{model}"
                    
                    if model_key not in processed_models:
                        processed_models.add(model_key)
                        
                        # Get or create the vehicle model
                        vehicle_model, created = VehicleModel.objects.get_or_create(
                            name=model,
                            company=company_map[make],
                            defaults={
                                'vehicle_type': type_map.get(drive),
                                'year_from': year,
                                'is_active': True
                            }
                        )
                        
                        if created:
                            self.stdout.write(f'Created vehicle model: {make} {model}')
                        else:
                            # Update existing model if needed
                            update_needed = False
                            if vehicle_model.vehicle_type != type_map.get(drive):
                                vehicle_model.vehicle_type = type_map.get(drive)
                                update_needed = True
                            if vehicle_model.year_from > year:
                                vehicle_model.year_from = year
                                update_needed = True
                            if update_needed:
                                vehicle_model.save()
                                self.stdout.write(f'Updated vehicle model: {make} {model}')
                            else:
                                self.stdout.write(f'Using existing model: {make} {model}')

            self.stdout.write(self.style.SUCCESS('Successfully imported vehicle data')) 