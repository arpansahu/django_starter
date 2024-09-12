"""
Django settings for django_starter project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
from decouple import config
import dj_database_url
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
import django
from django.db.models.signals import pre_init

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!

# ============================ENV VARIABLES=====================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', cast=bool, default=False)
ALLOWED_HOSTS = config('ALLOWED_HOSTS').split(' ')

AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME')
BUCKET_TYPE = config('BUCKET_TYPE')

DATABASE_URL = config('DATABASE_URL')
REDIS_CLOUD_URL = config('REDIS_CLOUD_URL')

MAIL_JET_API_KEY = config('MAIL_JET_API_KEY')
MAIL_JET_API_SECRET = config('MAIL_JET_API_SECRET')

DOMAIN = config('DOMAIN')
PROTOCOL = config('PROTOCOL')

SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT')  # production Or "staging", "development", etc.
SENTRY_DSH_URL = config('SENTRY_DSH_URL')

PROJECT_NAME = 'django_starter'
USE_S3 = True
# ===============================================================================

# Application definition

INSTALLED_APPS = [
    'daphne',    
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'account',
    'custom_tag_app',
    'check_service_health',
    'storages',  # Ensure django-storages is installed and added to apps
    'file_manager',

    # cleans up unused media, always in the end
    'django_cleanup.apps.CleanupConfig',

    # progress bar apps
    'channels',
    'django_celery_results',  # To store Celery task results
    'celery_progress_custom_app'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'django_starter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'django_starter.wsgi.application'
ASGI_APPLICATION = "django_starter.asgi.application"

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': config('DB_NAME'),
#         'USER': config('DB_USER'),
#         'PASSWORD': config('DB_PASSWORD'),
#         'HOST': config('DB_HOST'),
#         'PORT': config('DB_PORT'),
#     }
# }

# Parse database configuration from $DATABASE_URL

DATABASES = {'default': dj_database_url.config(default=DATABASE_URL)}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Kolkata'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/


if USE_S3:
    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'
else:
    AWS_S3_REGION_NAME = config('AWS_S3_REGION_NAME', default='us-east-1')

    # We have imported AWS_STORAGE_BUCKET_NAME, AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in the start of settings file

    AWS_S3_FILE_OVERWRITE = False  # Prevent overwriting files with the same name
    AWS_DEFAULT_ACL = None  # Ensure files are not public by default

    # Switch between MinIO and AWS S3
    if BUCKET_TYPE == 'MINIO':
        AWS_S3_ENDPOINT_URL = 'https://minio.arpansahu.me'
        AWS_S3_CUSTOM_DOMAIN = f'minio.arpansahu.me/{AWS_STORAGE_BUCKET_NAME}'
    elif BUCKET_TYPE == 'AWS':
        AWS_S3_ENDPOINT_URL = f'https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
        AWS_S3_CUSTOM_DOMAIN = AWS_S3_ENDPOINT_URL

    # Static and Media File Storage Settings
    AWS_STATIC_LOCATION = f'portfolio/{PROJECT_NAME}/static'
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_STATIC_LOCATION}/'
    
    AWS_PUBLIC_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/media'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_PUBLIC_MEDIA_LOCATION}/'
    
    AWS_PRIVATE_MEDIA_LOCATION = f'portfolio/{PROJECT_NAME}/private'

    # Use your custom storage classes
    STORAGES = {
        'default': {
            'BACKEND': f'{PROJECT_NAME}.storage_backends.PublicMediaStorage',
            'OPTIONS': {
                'location': AWS_PUBLIC_MEDIA_LOCATION,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
            },
        },
        'staticfiles': {
            'BACKEND': f'{PROJECT_NAME}.storage_backends.StaticStorage',
            'OPTIONS': {
                'location': AWS_STATIC_LOCATION,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
            },
        },
        'private': {
            'BACKEND': f'{PROJECT_NAME}.storage_backends.PrivateMediaStorage',
            'OPTIONS': {
                'location': AWS_PRIVATE_MEDIA_LOCATION,
                'bucket_name': AWS_STORAGE_BUCKET_NAME,
                'endpoint_url': AWS_S3_ENDPOINT_URL,
                'access_key': AWS_ACCESS_KEY_ID,
                'secret_key': AWS_SECRET_ACCESS_KEY,
                'default_acl': 'private',
                'custom_domain': False,  # Disable custom domain for private files
            },
        },
    }

    # Assign the custom storage backends to Django settings
    STATICFILES_STORAGE = f'{PROJECT_NAME}.storage_backends.StaticStorage'
    DEFAULT_FILE_STORAGE = f'{PROJECT_NAME}.storage_backends.PublicMediaStorage'

# Development settings (for local media/static handling)
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static"), ]


# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = "account.Account"

# Login_required Decorator
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

LOGIN_REDIRECT_URL = "/"


MAIL_JET_API_KEY = MAIL_JET_API_KEY
MAIL_JET_API_SECRET = MAIL_JET_API_SECRET

CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

#Caching
if not DEBUG:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_CLOUD_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': PROJECT_NAME
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'unique-snowflake',
        }
    }

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],  # Replace with your Redis server address
        },
    },
}

# Get the current git commit hash
def get_git_commit_hash():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
    except Exception:
        return None

sentry_sdk.init(
    dsn=SENTRY_DSH_URL,
    integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=True,
                signals_denylist=[
                    django.db.models.signals.pre_init,
                    django.db.models.signals.post_init,
                ],
                cache_spans=False,
            ),
        ],
    traces_sample_rate=1.0,  # Adjust this according to your needs
    send_default_pii=True,  # To capture personal identifiable information (optional)
    release=get_git_commit_hash(),  # Set the release to the current git commit hash
    environment=SENTRY_ENVIRONMENT,  # Or "staging", "development", etc.
    profiles_sample_rate=1.0,
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'sentry': {
            'level': 'ERROR',  # Change this to WARNING or INFO if needed
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'sentry'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'sentry'],
            'level': 'ERROR',  # Only log errors to Sentry
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console', 'sentry'],
            'level': 'ERROR',  # Only log errors to Sentry
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'sentry'],
            'level': 'WARNING',  # You can set this to INFO or DEBUG as needed
            'propagate': False,
        },
        # You can add more loggers here if needed
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
    },
}

CSRF_TRUSTED_ORIGINS = ['https://django-starter.arpansahu.me']