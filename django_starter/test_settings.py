"""
Test Settings for Django Starter

Uses SQLite in-memory database for faster test execution.
"""
from .settings import *

# Use SQLite for tests - much faster than PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable password hashers for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging during tests
LOGGING = {}

# Use a simple email backend
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Disable Celery during tests
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Disable debug
DEBUG = False

# Use faster storage
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
