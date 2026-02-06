# check_service_health/management/commands/test_celery.py

from django.core.management.base import BaseCommand
from celery import Celery
from django.conf import settings
from celery.result import AsyncResult
import time


class Command(BaseCommand):
    help = 'Test if Celery is working properly'

    def handle(self, *args, **kwargs):
        try:
            # Create Celery app instance
            app = Celery('django_starter')
            app.config_from_object('django.conf:settings', namespace='CELERY')
            
            # Check if Celery is configured
            self.stdout.write(f'Celery Broker URL: {settings.CELERY_BROKER_URL[:30]}...')
            
            # Try to inspect Celery workers
            inspect = app.control.inspect()
            
            # Check active workers
            active_workers = inspect.active()
            if active_workers:
                self.stdout.write(self.style.SUCCESS(f'Active Celery workers found: {list(active_workers.keys())}'))
            else:
                self.stdout.write(self.style.WARNING('No active Celery workers found'))
            
            # Check registered tasks
            registered_tasks = inspect.registered()
            if registered_tasks:
                self.stdout.write(self.style.SUCCESS(f'Registered tasks: {len(sum(registered_tasks.values(), []))} tasks'))
            else:
                self.stdout.write(self.style.WARNING('No registered tasks found'))
            
            # Try to send a simple task
            try:
                from django_starter.tasks import demo_task
                self.stdout.write('Attempting to queue demo_task...')
                
                result = demo_task.apply_async()
                self.stdout.write(self.style.SUCCESS(f'Task queued successfully with ID: {result.id}'))
                
                # Wait a bit and check task state
                time.sleep(2)
                async_result = AsyncResult(result.id, app=app)
                self.stdout.write(f'Task state after 2 seconds: {async_result.state}')
                
                if async_result.state == 'SUCCESS':
                    self.stdout.write(self.style.SUCCESS('Celery is working correctly - task completed'))
                elif async_result.state == 'PENDING':
                    self.stdout.write(self.style.WARNING('Task is still pending - workers may be slow or offline'))
                else:
                    self.stdout.write(self.style.WARNING(f'Task state: {async_result.state}'))
                    
            except ImportError:
                self.stdout.write(self.style.WARNING('demo_task not found, skipping task execution test'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error executing task: {e}'))
            
            self.stdout.write(self.style.SUCCESS('Celery connectivity test completed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
