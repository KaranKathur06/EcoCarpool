from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Lists all users in the database'

    def handle(self, *args, **options):
        users = CustomUser.objects.all()
        if not users:
            self.stdout.write('No users found in the database.')
            return
            
        for user in users:
            self.stdout.write(f'Username: {user.username}')
            self.stdout.write(f'Email: {user.email}')
            self.stdout.write(f'Role: {user.role}')
            self.stdout.write(f'Phone: {user.phone_number}')
            self.stdout.write('-' * 50) 