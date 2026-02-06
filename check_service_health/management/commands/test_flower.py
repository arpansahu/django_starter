# check_service_health/management/commands/test_flower.py

from django.core.management.base import BaseCommand
import requests
from django.conf import settings


class Command(BaseCommand):
    help = 'Test if Flower (Celery monitoring) is accessible'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            default='http://localhost:5555',
            help='Flower URL to test (default: http://localhost:5555)'
        )

    def handle(self, *args, **kwargs):
        flower_url = kwargs.get('url')
        
        try:
            self.stdout.write(f'Testing Flower at: {flower_url}')
            
            # Test Flower API endpoints
            endpoints = [
                ('/', 'Dashboard'),
                ('/api/workers', 'Workers API'),
                ('/api/tasks', 'Tasks API'),
            ]
            
            all_success = True
            
            for endpoint, name in endpoints:
                try:
                    response = requests.get(f'{flower_url}{endpoint}', timeout=5)
                    
                    if response.status_code == 200:
                        self.stdout.write(self.style.SUCCESS(f'✓ {name} is accessible (Status: {response.status_code})'))
                    elif response.status_code == 401:
                        self.stdout.write(self.style.WARNING(f'⚠ {name} requires authentication (Status: {response.status_code})'))
                    else:
                        self.stdout.write(self.style.WARNING(f'⚠ {name} returned status: {response.status_code}'))
                        all_success = False
                        
                except requests.exceptions.ConnectionError:
                    self.stdout.write(self.style.ERROR(f'✗ {name} - Connection refused. Is Flower running?'))
                    all_success = False
                except requests.exceptions.Timeout:
                    self.stdout.write(self.style.ERROR(f'✗ {name} - Request timed out'))
                    all_success = False
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'✗ {name} - Error: {e}'))
                    all_success = False
            
            if all_success:
                self.stdout.write(self.style.SUCCESS('Flower is working correctly'))
            else:
                self.stdout.write(self.style.WARNING('Some Flower endpoints are not accessible'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
