from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Cleans up all vehicle tables'

    def handle(self, *args, **kwargs):
        cursor = connection.cursor()
        
        # List of tables to drop
        tables_to_drop = [
            'vehicle_type',
            'vehicle_company',
            'vehicle_model',
            'vehicles_vehiclebrand',
            'vehicles_vehiclecompany',
            'vehicles_vehiclemodel',
            'vehicles_vehicletype'
        ]
        
        # Drop each table
        for table in tables_to_drop:
            try:
                cursor.execute(f'DROP TABLE IF EXISTS {table}')
                self.stdout.write(self.style.SUCCESS(f'Dropped table: {table}'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error dropping table {table}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('Successfully cleaned up all vehicle tables')) 