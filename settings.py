AUTH_USER_MODEL = 'users.CustomUser'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'ecocarpool',
        'USER': 'root',
        'PASSWORD': '',  # your database password if you have one
        'HOST': 'localhost',
        'PORT': '3306',
    }
} 