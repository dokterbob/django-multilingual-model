DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

INSTALLED_APPS = [
    'multilingual_model'
]

SITE_ID = 1

# Enable time-zone support for Django 1.4 (ignored in older versions)
USE_TZ = True

# Generate random secret key
import random
SECRET_KEY = ''.join([
    random.SystemRandom().choice(
        'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    ) for i in range(50)
])
