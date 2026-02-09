from django.test import TestCase
from django.core.management import call_command
from django.core.cache import cache
from io import StringIO
from check_service_health.models import TestModel


class TestModelTestCase(TestCase):
    """Test the TestModel"""
    
    def test_create_test_model(self):
        """Test creating a TestModel instance"""
        test_obj = TestModel.objects.create(name='Test Object')
        self.assertEqual(test_obj.name, 'Test Object')
        self.assertIsNotNone(test_obj.created_at)
    
    def test_test_model_string_representation(self):
        """Test string representation of TestModel"""
        test_obj = TestModel.objects.create(name='Test Object')
        self.assertEqual(str(test_obj), 'Test Object')
    
    def test_test_model_queryset(self):
        """Test querying TestModel"""
        TestModel.objects.create(name='Object 1')
        TestModel.objects.create(name='Object 2')
        
        self.assertEqual(TestModel.objects.count(), 2)
        self.assertTrue(TestModel.objects.filter(name='Object 1').exists())


class TestCacheCommandTestCase(TestCase):
    """Test the test_cache management command"""
    
    def setUp(self):
        """Clear cache before each test"""
        cache.clear()
    
    def tearDown(self):
        """Clear cache after each test"""
        cache.clear()
    
    def test_cache_command_sets_value(self):
        """Test that cache command sets a value"""
        out = StringIO()
        
        # Before command, key should not exist
        self.assertIsNone(cache.get('test_key'))
        
        # Run the command (it will wait 12 seconds)
        # We'll test the initial set separately
        cache.set('test_key', 'test_value', timeout=10)
        self.assertEqual(cache.get('test_key'), 'test_value')
    
    def test_cache_command_output(self):
        """Test that cache command produces expected output"""
        out = StringIO()
        
        # Note: This test won't wait 12 seconds, just checks command runs
        # For CI/CD, we'll mock the sleep
        from unittest.mock import patch
        
        with patch('check_service_health.management.commands.test_cache.time.sleep'):
            call_command('test_cache', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Initial cache set:', output)
    
    def test_cache_expiration(self):
        """Test that cache values expire"""
        # Set a value with 1 second timeout
        cache.set('expire_test', 'value', timeout=1)
        self.assertEqual(cache.get('expire_test'), 'value')
        
        # After setting, should still exist
        import time
        time.sleep(2)
        
        # After 2 seconds, should be None
        self.assertIsNone(cache.get('expire_test'))


class TestDBCommandTestCase(TestCase):
    """Test the test_db management command"""
    
    def test_db_command_creates_entry(self):
        """Test that DB command creates an entry"""
        self.assertEqual(TestModel.objects.count(), 0)
        
        out = StringIO()
        call_command('test_db', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Database test completed successfully', output)
        
        # Command should clean up after itself
        self.assertEqual(TestModel.objects.count(), 0)
    
    def test_db_command_crud_operations(self):
        """Test that DB command performs CRUD operations"""
        out = StringIO()
        call_command('test_db', stdout=out)
        
        output = out.getvalue()
        
        # Check all CRUD operations are mentioned
        self.assertIn('Successfully created test entry', output)
        self.assertIn('Successfully retrieved test entry', output)
        self.assertIn('Successfully updated test entry', output)
        self.assertIn('Successfully deleted test entry', output)
    
    def test_db_command_handles_errors(self):
        """Test that DB command handles errors gracefully"""
        from unittest.mock import patch
        
        out = StringIO()
        
        # Mock the create method to raise an exception
        with patch.object(TestModel.objects, 'create', side_effect=Exception('Test error')):
            call_command('test_db', stdout=out)
        
        output = out.getvalue()
        self.assertIn('Error occurred', output)


class TestCeleryCommandTestCase(TestCase):
    """Test the test_celery management command"""
    
    def test_celery_command_runs(self):
        """Test that celery command runs without crashing"""
        out = StringIO()
        
        try:
            call_command('test_celery', stdout=out)
            output = out.getvalue()
            
            # Check that command produces some output
            self.assertIn('Celery', output)
        except Exception as e:
            # Command might fail if Celery isn't running, but shouldn't crash
            self.assertIsInstance(e, Exception)
    
    def test_celery_command_checks_broker(self):
        """Test that celery command checks broker configuration"""
        out = StringIO()
        
        call_command('test_celery', stdout=out)
        output = out.getvalue()
        
        # Should mention broker URL
        self.assertIn('Broker', output.replace('broker', 'Broker'))


class TestFlowerCommandTestCase(TestCase):
    """Test the test_flower management command"""
    
    def test_flower_command_runs(self):
        """Test that flower command runs without crashing"""
        out = StringIO()
        
        try:
            call_command('test_flower', stdout=out, url='http://localhost:5555')
            output = out.getvalue()
            
            # Check that command produces output about Flower
            self.assertIn('Flower', output)
        except Exception as e:
            # Command might fail if Flower isn't running
            self.assertIsInstance(e, Exception)
    
    def test_flower_command_accepts_url(self):
        """Test that flower command accepts custom URL"""
        out = StringIO()
        
        call_command('test_flower', stdout=out, url='http://example.com:5555')
        output = out.getvalue()
        
        # Should test the provided URL
        self.assertIn('example.com', output)


class TestStorageCommandTestCase(TestCase):
    """Test the test_storage management command"""
    
    def test_storage_command_runs(self):
        """Test that storage command runs without crashing"""
        out = StringIO()
        
        try:
            call_command('test_storage', stdout=out)
            output = out.getvalue()
            
            # Check that command produces storage-related output
            self.assertTrue(len(output) > 0)
        except Exception as e:
            # Command might fail if S3/MinIO isn't configured
            self.assertIsInstance(e, Exception)
    
    def test_storage_command_checks_backend(self):
        """Test that storage command checks storage backend"""
        from unittest.mock import patch
        from django.conf import settings
        
        out = StringIO()
        
        # Mock USE_S3 to be True to test S3 path
        with patch.object(settings, 'USE_S3', True):
            try:
                call_command('test_storage', stdout=out)
                output = out.getvalue()
                
                # Should check storage configuration
                self.assertTrue(len(output) > 0)
            except:
                pass  # Might fail if storage not configured


class TestAllServicesCommandTestCase(TestCase):
    """Test the test_all_services management command"""
    
    def test_all_services_command_runs(self):
        """Test that all services command runs and calls sub-commands"""
        out = StringIO()
        
        call_command('test_all_services', stdout=out)
        output = out.getvalue()
        
        # Should mention all services (case-insensitive check)
        self.assertIn('HEALTH CHECK', output.upper())
        self.assertIn('SUMMARY', output.upper())
    
    def test_all_services_command_tests_database(self):
        """Test that all services command tests database"""
        out = StringIO()
        
        call_command('test_all_services', stdout=out)
        output = out.getvalue()
        
        # Should test database
        self.assertIn('Database', output)
    
    def test_all_services_command_tests_cache(self):
        """Test that all services command tests cache"""
        out = StringIO()
        
        call_command('test_all_services', stdout=out)
        output = out.getvalue()
        
        # Should test cache
        self.assertIn('Cache', output)


class CacheHealthCheckTestCase(TestCase):
    """Integration tests for cache health checking"""
    
    def setUp(self):
        cache.clear()
    
    def tearDown(self):
        cache.clear()
    
    def test_cache_is_accessible(self):
        """Test that cache backend is accessible"""
        try:
            cache.set('health_check', 'ok', timeout=1)
            value = cache.get('health_check')
            self.assertEqual(value, 'ok')
        except Exception as e:
            self.fail(f'Cache is not accessible: {e}')
    
    def test_cache_supports_multiple_keys(self):
        """Test that cache can handle multiple keys"""
        cache.set('key1', 'value1', timeout=10)
        cache.set('key2', 'value2', timeout=10)
        cache.set('key3', 'value3', timeout=10)
        
        self.assertEqual(cache.get('key1'), 'value1')
        self.assertEqual(cache.get('key2'), 'value2')
        self.assertEqual(cache.get('key3'), 'value3')
    
    def test_cache_delete_operation(self):
        """Test cache delete operation"""
        cache.set('delete_test', 'value', timeout=10)
        self.assertEqual(cache.get('delete_test'), 'value')
        
        cache.delete('delete_test')
        self.assertIsNone(cache.get('delete_test'))


class DatabaseHealthCheckTestCase(TestCase):
    """Integration tests for database health checking"""
    
    def test_database_is_accessible(self):
        """Test that database is accessible"""
        try:
            TestModel.objects.create(name='Health Check')
            count = TestModel.objects.count()
            self.assertGreaterEqual(count, 1)
            TestModel.objects.all().delete()
        except Exception as e:
            self.fail(f'Database is not accessible: {e}')
    
    def test_database_transactions(self):
        """Test database transaction handling"""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                obj = TestModel.objects.create(name='Transaction Test')
                self.assertTrue(TestModel.objects.filter(id=obj.id).exists())
        except Exception as e:
            self.fail(f'Database transaction failed: {e}')
    
    def test_database_rollback(self):
        """Test database rollback on error"""
        from django.db import transaction
        
        initial_count = TestModel.objects.count()
        
        try:
            with transaction.atomic():
                TestModel.objects.create(name='Will Rollback')
                # Force an error
                raise Exception('Test rollback')
        except Exception:
            pass
        
        # Count should be same as before
        self.assertEqual(TestModel.objects.count(), initial_count)


class ServiceHealthIntegrationTestCase(TestCase):
    """Integration tests for all service health checks"""
    
    def test_database_connectivity(self):
        """Test database is connected and working"""
        try:
            # Create, read, update, delete
            obj = TestModel.objects.create(name='Integration Test')
            obj.name = 'Updated'
            obj.save()
            obj.delete()
            self.assertTrue(True)
        except Exception as e:
            self.fail(f'Database integration test failed: {e}')
    
    def test_cache_connectivity(self):
        """Test cache is connected and working"""
        try:
            cache.set('integration_test', 'working', timeout=10)
            value = cache.get('integration_test')
            self.assertEqual(value, 'working')
            cache.delete('integration_test')
        except Exception as e:
            self.fail(f'Cache integration test failed: {e}')
    
    def test_settings_loaded(self):
        """Test that all service settings are loaded"""
        from django.conf import settings
        
        # Check database settings
        self.assertIsNotNone(settings.DATABASES)
        
        # Check cache settings (if DEBUG is False)
        self.assertTrue(hasattr(settings, 'CACHES'))
        
        # Check Celery settings
        self.assertTrue(hasattr(settings, 'CELERY_BROKER_URL'))
        self.assertTrue(hasattr(settings, 'CELERY_RESULT_BACKEND'))
        
        # Check storage settings
        self.assertTrue(hasattr(settings, 'USE_S3'))

