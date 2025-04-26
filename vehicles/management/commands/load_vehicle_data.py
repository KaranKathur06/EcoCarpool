from django.core.management.base import BaseCommand
from vehicles.models import VehicleType, VehicleCompany, VehicleModel

class Command(BaseCommand):
    help = 'Loads initial vehicle data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Loading vehicle data...')

        # Create vehicle types
        vehicle_types = {
            'Luxury': 'High-end vehicles with premium features and superior comfort',
            'Sports': 'High-performance vehicles designed for speed and handling',
            'SUV': 'Sport Utility Vehicles combining luxury with practicality',
            'Sedan': 'Four-door passenger cars with separate trunk compartment',
            'Coupe': 'Two-door sporty vehicles with sleek design',
            'Convertible': 'Vehicles with retractable roof',
            'Electric': 'Fully electric powered vehicles',
            'Hybrid': 'Vehicles combining gasoline and electric power'
        }

        type_objects = {}
        for type_name, description in vehicle_types.items():
            vtype, created = VehicleType.objects.get_or_create(
                type_name=type_name,
                defaults={'description': description}
            )
            type_objects[type_name] = vtype
            self.stdout.write(f'Created vehicle type: {type_name}')

        # Create companies
        companies = [
            ('BMW', True, 'Germany'),
            ('Mercedes-Benz', True, 'Germany'),
            ('Audi', True, 'Germany'),
            ('Lexus', True, 'Japan'),
            ('Porsche', True, 'Germany'),
            ('Rolls-Royce', True, 'United Kingdom'),
            ('Bentley', True, 'United Kingdom'),
            ('Jaguar', True, 'United Kingdom'),
            ('Land Rover', True, 'United Kingdom'),
            ('Maserati', True, 'Italy'),
            ('Tesla', True, 'United States'),
            ('Genesis', True, 'South Korea'),
            ('Lamborghini', True, 'Italy'),
            ('Ferrari', True, 'Italy'),
            ('Aston Martin', True, 'United Kingdom'),
            ('McLaren', True, 'United Kingdom'),
            ('Bugatti', True, 'France'),
            ('Maybach', True, 'Germany'),
            ('Lotus', True, 'United Kingdom'),
            ('Alfa Romeo', True, 'Italy')
        ]

        company_objects = {}
        for name, is_luxury, country in companies:
            company, created = VehicleCompany.objects.get_or_create(
                company_name=name,
                defaults={
                    'is_luxury': is_luxury,
                    'country_of_origin': country
                }
            )
            company_objects[name] = company
            self.stdout.write(f'Created company: {name}')

        # Create models
        models = [
            # BMW Models
            ('3 Series', 'BMW', 'Sedan', 2020, None, 41450.00),
            ('5 Series', 'BMW', 'Sedan', 2020, None, 54800.00),
            ('7 Series', 'BMW', 'Luxury', 2020, None, 86800.00),
            ('X3', 'BMW', 'SUV', 2020, None, 43000.00),
            ('X5', 'BMW', 'SUV', 2020, None, 59400.00),
            ('X7', 'BMW', 'SUV', 2020, None, 74900.00),
            ('M3', 'BMW', 'Sports', 2020, None, 69900.00),
            ('M5', 'BMW', 'Sports', 2020, None, 103500.00),
            ('i4', 'BMW', 'Electric', 2021, None, 55400.00),
            ('iX', 'BMW', 'Electric', 2021, None, 84100.00),

            # Mercedes-Benz Models
            ('C-Class', 'Mercedes-Benz', 'Sedan', 2020, None, 41600.00),
            ('E-Class', 'Mercedes-Benz', 'Sedan', 2020, None, 54250.00),
            ('S-Class', 'Mercedes-Benz', 'Luxury', 2020, None, 94250.00),
            ('GLC', 'Mercedes-Benz', 'SUV', 2020, None, 43200.00),
            ('GLE', 'Mercedes-Benz', 'SUV', 2020, None, 57200.00),
            ('GLS', 'Mercedes-Benz', 'SUV', 2020, None, 77850.00),
            ('AMG GT', 'Mercedes-Benz', 'Sports', 2020, None, 99950.00),
            ('EQS', 'Mercedes-Benz', 'Electric', 2021, None, 102310.00),

            # Audi Models
            ('A4', 'Audi', 'Sedan', 2020, None, 39100.00),
            ('A6', 'Audi', 'Sedan', 2020, None, 54900.00),
            ('A8', 'Audi', 'Luxury', 2020, None, 86500.00),
            ('Q5', 'Audi', 'SUV', 2020, None, 43300.00),
            ('Q7', 'Audi', 'SUV', 2020, None, 55800.00),
            ('Q8', 'Audi', 'SUV', 2020, None, 70300.00),
            ('RS6', 'Audi', 'Sports', 2020, None, 109000.00),
            ('e-tron', 'Audi', 'Electric', 2020, None, 65900.00),

            # Tesla Models
            ('Model S', 'Tesla', 'Electric', 2020, None, 79990.00),
            ('Model 3', 'Tesla', 'Electric', 2020, None, 46990.00),
            ('Model X', 'Tesla', 'Electric', 2020, None, 89990.00),
            ('Model Y', 'Tesla', 'Electric', 2020, None, 53990.00),

            # Porsche Models
            ('911', 'Porsche', 'Sports', 2020, None, 101200.00),
            ('Taycan', 'Porsche', 'Electric', 2020, None, 82700.00),
            ('Panamera', 'Porsche', 'Sedan', 2020, None, 87200.00),
            ('Cayenne', 'Porsche', 'SUV', 2020, None, 69000.00),
            ('Macan', 'Porsche', 'SUV', 2020, None, 54900.00)
        ]

        for model_name, company_name, type_name, year_from, year_to, price in models:
            model, created = VehicleModel.objects.get_or_create(
                model_name=model_name,
                company=company_objects[company_name],
                type=type_objects[type_name],
                defaults={
                    'year_from': year_from,
                    'year_to': year_to,
                    'base_price': price,
                    'is_active': True
                }
            )
            self.stdout.write(f'Created model: {company_name} {model_name}')

        self.stdout.write(self.style.SUCCESS('Successfully loaded vehicle data')) 