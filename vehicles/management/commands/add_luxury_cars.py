from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleCompany, VehicleModel

class Command(BaseCommand):
    help = 'Adds luxury car types and models'

    def handle(self, *args, **kwargs):
        # Add Luxury Car type
        luxury_type, created = VehicleType.objects.get_or_create(
            name='Luxury Car',
            defaults={'description': 'High-end luxury vehicles with premium features'}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Created Luxury Car type'))
        else:
            self.stdout.write('Luxury Car type already exists')

        # Add luxury car companies
        companies = {
            'Mercedes-Benz': 'Germany',
            'BMW': 'Germany',
            'Audi': 'Germany',
            'Lexus': 'Japan',
            'Rolls-Royce': 'United Kingdom'
        }

        for name, country in companies.items():
            company, created = VehicleCompany.objects.get_or_create(
                name=name,
                defaults={
                    'country': country,
                    'website': f'https://www.{name.lower().replace("-", "").replace(" ", "")}.com'
                }
            )
            
            if created:
                self.stdout.write(f'Created company: {name}')
            else:
                self.stdout.write(f'Company already exists: {name}')

            # Add models for each company
            if name == 'Mercedes-Benz':
                models = ['S-Class', 'E-Class', 'GLS']
            elif name == 'BMW':
                models = ['7 Series', '5 Series', 'X7']
            elif name == 'Audi':
                models = ['A8', 'A6', 'Q8']
            elif name == 'Lexus':
                models = ['LS', 'ES', 'LX']
            elif name == 'Rolls-Royce':
                models = ['Phantom', 'Ghost', 'Cullinan']

            for model_name in models:
                model, created = VehicleModel.objects.get_or_create(
                    company=company,
                    name=model_name,
                    defaults={
                        'vehicle_type': luxury_type,
                        'year_from': 2020,
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f'Created model: {company.name} {model_name}')
                else:
                    self.stdout.write(f'Model already exists: {company.name} {model_name}') 