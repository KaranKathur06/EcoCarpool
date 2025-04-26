from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from .models import CustomUser

class CustomAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None
            
        try:
            # Convert username to lowercase for case-insensitive comparison
            username = username.lower().strip()
            
            # Try to find a user that matches either email, phone number, or username
            user = CustomUser.objects.get(
                Q(email__iexact=username) | 
                Q(phone_number=username) |
                Q(username__iexact=username)
            )
            
            if user.check_password(password):
                return user
            return None  # Password doesn't match
            
        except CustomUser.DoesNotExist:
            # Run the password hasher even if user doesn't exist to prevent timing attacks
            CustomUser().set_password(password)
            return None
        except Exception:
            # Log any other unexpected errors
            return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None 