# check_service_health/management/commands/test_storage.py

from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage, storages
from django.core.files.base import ContentFile
from django.conf import settings
import uuid


class Command(BaseCommand):
    help = 'Test if MinIO/S3 storage is working properly'

    def handle(self, *args, **kwargs):
        try:
            # Check if using S3/MinIO
            if not getattr(settings, 'USE_S3', False):
                self.stdout.write(self.style.WARNING('USE_S3 is False - using local storage'))
                return
            
            self.stdout.write(f'Storage Backend: {settings.STORAGES["default"]["BACKEND"]}')
            self.stdout.write(f'Bucket Type: {settings.BUCKET_TYPE}')
            self.stdout.write(f'Bucket Name: {settings.AWS_STORAGE_BUCKET_NAME}')
            self.stdout.write(f'Endpoint URL: {settings.AWS_S3_ENDPOINT_URL}')
            
            # Test default storage (public media)
            self.stdout.write('\n--- Testing Default Storage (Public Media) ---')
            self._test_storage('default', 'Default Storage')
            
            # Test private storage
            self.stdout.write('\n--- Testing Private Storage ---')
            self._test_storage('private', 'Private Storage')
            
            # Test static files storage
            self.stdout.write('\n--- Testing Static Files Storage ---')
            self._test_storage('staticfiles', 'Static Files Storage')
            
            self.stdout.write(self.style.SUCCESS('\nStorage test completed successfully'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error occurred: {e}'))
    
    def _test_storage(self, storage_name, display_name):
        """Test a specific storage backend"""
        try:
            # Get storage instance
            storage = storages[storage_name]
            
            # Generate unique filename
            test_filename = f'health-check-{uuid.uuid4()}.txt'
            test_content = f'Health check test file - {uuid.uuid4()}'
            
            # Test 1: Write file
            self.stdout.write(f'Writing test file: {test_filename}')
            file_path = storage.save(test_filename, ContentFile(test_content.encode()))
            self.stdout.write(self.style.SUCCESS(f'✓ File saved at: {file_path}'))
            
            # Test 2: Check file exists
            if storage.exists(file_path):
                self.stdout.write(self.style.SUCCESS(f'✓ File exists verification passed'))
            else:
                self.stdout.write(self.style.ERROR(f'✗ File exists check failed'))
                return
            
            # Test 3: Read file
            with storage.open(file_path, 'r') as f:
                content = f.read()
                if test_content in content:
                    self.stdout.write(self.style.SUCCESS(f'✓ File content verification passed'))
                else:
                    self.stdout.write(self.style.ERROR(f'✗ File content mismatch'))
            
            # Test 4: Get file URL
            try:
                url = storage.url(file_path)
                self.stdout.write(self.style.SUCCESS(f'✓ File URL generated: {url[:50]}...'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'⚠ URL generation error: {e}'))
            
            # Test 5: Get file size
            size = storage.size(file_path)
            self.stdout.write(self.style.SUCCESS(f'✓ File size: {size} bytes'))
            
            # Test 6: Delete file (cleanup)
            storage.delete(file_path)
            if not storage.exists(file_path):
                self.stdout.write(self.style.SUCCESS(f'✓ File deleted successfully'))
            else:
                self.stdout.write(self.style.WARNING(f'⚠ File deletion verification failed'))
            
            self.stdout.write(self.style.SUCCESS(f'{display_name} test passed'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ {display_name} test failed: {e}'))
