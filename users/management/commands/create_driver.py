from django.core.management.base import BaseCommand
from users.models import CustomUser

class Command(BaseCommand):
    help = 'Creates a driver user'

    def handle(self, *args, **kwargs):
        try:
            user = CustomUser.objects.create_user(
                username='driver1',
                email='driver1@example.com',
                password='driver123',
                role='driver',
                phone_number='+1234567891'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created driver user: {user.username}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating driver user: {str(e)}')) 