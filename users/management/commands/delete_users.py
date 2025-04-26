from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Deletes all users from the database'

    def handle(self, *args, **options):
        user_count = CustomUser.objects.count()
        if user_count == 0:
            self.stdout.write('No users found in the database.')
            return
            
        self.stdout.write(f'Found {user_count} users in the database.')
        CustomUser.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all users from the database.')) 