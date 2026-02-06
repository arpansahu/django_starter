import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_starter.settings')

app = Celery('django_starter')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure broker connection retry on startup for Celery 6.0+ compatibility
app.conf.broker_connection_retry_on_startup = True

app.autodiscover_tasks()
