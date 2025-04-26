from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes vehicle tables and adds initial data'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_type (
                    id bigint AUTO_INCREMENT PRIMARY KEY,
                    type_name varchar(100) NOT NULL,
                    description text NOT NULL
                );
            """)
            
            # Insert vehicle types
            cursor.execute("""
                INSERT IGNORE INTO vehicle_type (type_name, description) VALUES
                ('Sedan', 'A passenger car with a three-box configuration'),
                ('SUV', 'Sport Utility Vehicle with higher ground clearance'),
                ('Hatchback', 'A car with a rear door that opens upwards'),
                ('Luxury', 'High-end vehicles with premium features');
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_company (
                    id bigint AUTO_INCREMENT PRIMARY KEY,
                    company_name varchar(100) NOT NULL,
                    is_luxury boolean NOT NULL,
                    country_of_origin varchar(100) NOT NULL
                );
            """)
            
            # Insert vehicle companies
            cursor.execute("""
                INSERT IGNORE INTO vehicle_company (company_name, is_luxury, country_of_origin) VALUES
                ('Toyota', 0, 'Japan'),
                ('Honda', 0, 'Japan'),
                ('BMW', 1, 'Germany'),
                ('Mercedes-Benz', 1, 'Germany');
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_model (
                    id bigint AUTO_INCREMENT PRIMARY KEY,
                    model_name varchar(100) NOT NULL,
                    year_from integer NOT NULL,
                    year_to integer NULL,
                    base_price decimal(10,2) NULL,
                    is_active boolean NOT NULL,
                    company_id bigint NOT NULL,
                    type_id bigint NOT NULL,
                    FOREIGN KEY (company_id) REFERENCES vehicle_company(id),
                    FOREIGN KEY (type_id) REFERENCES vehicle_type(id)
                );
            """)
            
            self.stdout.write(self.style.SUCCESS('Successfully fixed vehicle tables')) 