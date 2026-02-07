"""
Management Command: health_check

Performs comprehensive health checks on the system.
Demonstrates integration with multiple services.
"""
import socket
import time
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import connection
from django.core.cache import cache
from commands_app.models import SystemMetric


class Command(BaseCommand):
    help = 'Perform comprehensive system health checks'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--checks',
            nargs='+',
            default=['database', 'cache', 'storage'],
            help='Health checks to perform (database, cache, storage, celery, all)',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=5,
            help='Timeout for each check in seconds (default: 5)',
        )
        parser.add_argument(
            '--verbose-output',
            action='store_true',
            help='Show detailed output',
        )
        parser.add_argument(
            '--fail-fast',
            action='store_true',
            help='Stop on first failure',
        )
        parser.add_argument(
            '--json',
            action='store_true',
            help='Output results as JSON',
        )
    
    def handle(self, *args, **options):
        checks = options['checks']
        timeout = options['timeout']
        verbose = options['verbose_output']
        fail_fast = options['fail_fast']
        output_json = options['json']
        
        if 'all' in checks:
            checks = ['database', 'cache', 'storage', 'celery', 'email']
        
        self.stdout.write(f'🏥 Running health checks...\n')
        
        results = {}
        all_passed = True
        
        for check in checks:
            try:
                start_time = time.time()
                
                if check == 'database':
                    passed, message = self._check_database(timeout, verbose)
                elif check == 'cache':
                    passed, message = self._check_cache(timeout, verbose)
                elif check == 'storage':
                    passed, message = self._check_storage(timeout, verbose)
                elif check == 'celery':
                    passed, message = self._check_celery(timeout, verbose)
                elif check == 'email':
                    passed, message = self._check_email(timeout, verbose)
                else:
                    self.stdout.write(self.style.WARNING(f'Unknown check: {check}'))
                    continue
                
                duration = time.time() - start_time
                
                results[check] = {
                    'passed': passed,
                    'message': message,
                    'duration_ms': round(duration * 1000, 2),
                }
                
                if passed:
                    self.stdout.write(self.style.SUCCESS(
                        f'  ✅ {check}: {message} ({duration*1000:.0f}ms)'
                    ))
                else:
                    self.stdout.write(self.style.ERROR(
                        f'  ❌ {check}: {message} ({duration*1000:.0f}ms)'
                    ))
                    all_passed = False
                    
                    if fail_fast:
                        break
                        
            except Exception as e:
                results[check] = {
                    'passed': False,
                    'message': str(e),
                    'duration_ms': 0,
                }
                self.stdout.write(self.style.ERROR(f'  ❌ {check}: {e}'))
                all_passed = False
                
                if fail_fast:
                    break
        
        # Summary
        self.stdout.write('')
        
        if output_json:
            import json
            self.stdout.write(json.dumps(results, indent=2))
        
        passed_count = sum(1 for r in results.values() if r['passed'])
        total_count = len(results)
        
        if all_passed:
            self.stdout.write(self.style.SUCCESS(
                f'✅ All health checks passed ({passed_count}/{total_count})'
            ))
        else:
            self.stdout.write(self.style.ERROR(
                f'❌ Health checks failed ({passed_count}/{total_count} passed)'
            ))
            raise CommandError('Health checks failed')
    
    def _check_database(self, timeout: int, verbose: bool):
        """Check database connectivity"""
        try:
            with connection.cursor() as cursor:
                cursor.execute('SELECT 1')
                result = cursor.fetchone()
            
            if verbose:
                self.stdout.write(f'     Database: {settings.DATABASES["default"]["ENGINE"]}')
            
            return True, 'Connected'
        except Exception as e:
            return False, str(e)
    
    def _check_cache(self, timeout: int, verbose: bool):
        """Check cache connectivity"""
        try:
            test_key = '_health_check_test'
            test_value = 'test_value'
            
            cache.set(test_key, test_value, 10)
            retrieved = cache.get(test_key)
            cache.delete(test_key)
            
            if retrieved != test_value:
                return False, 'Cache read/write mismatch'
            
            if verbose:
                cache_backend = settings.CACHES.get('default', {}).get('BACKEND', 'unknown')
                self.stdout.write(f'     Cache: {cache_backend}')
            
            return True, 'Read/write OK'
        except Exception as e:
            return False, str(e)
    
    def _check_storage(self, timeout: int, verbose: bool):
        """Check storage/file system"""
        import os
        import tempfile
        
        try:
            # Check media root
            media_root = getattr(settings, 'MEDIA_ROOT', None)
            if media_root:
                if not os.path.exists(media_root):
                    return False, f'MEDIA_ROOT does not exist: {media_root}'
                if not os.access(media_root, os.W_OK):
                    return False, f'MEDIA_ROOT not writable: {media_root}'
            
            # Test file write
            with tempfile.NamedTemporaryFile(delete=True) as f:
                f.write(b'test')
                f.flush()
            
            if verbose:
                self.stdout.write(f'     Media root: {media_root or "not configured"}')
            
            return True, 'Storage accessible'
        except Exception as e:
            return False, str(e)
    
    def _check_celery(self, timeout: int, verbose: bool):
        """Check Celery connectivity"""
        try:
            from django_starter.celery import app
            
            # Check broker connection
            inspect = app.control.inspect(timeout=timeout)
            stats = inspect.stats()
            
            if not stats:
                return False, 'No Celery workers responding'
            
            worker_count = len(stats)
            
            if verbose:
                for worker, info in stats.items():
                    self.stdout.write(f'     Worker: {worker}')
            
            return True, f'{worker_count} worker(s) active'
        except ImportError:
            return False, 'Celery not configured'
        except Exception as e:
            return False, str(e)
    
    def _check_email(self, timeout: int, verbose: bool):
        """Check email configuration"""
        try:
            email_host = getattr(settings, 'EMAIL_HOST', None)
            
            if not email_host:
                return True, 'Email not configured (OK)'
            
            # Try to connect to SMTP server
            port = getattr(settings, 'EMAIL_PORT', 587)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((email_host, port))
            sock.close()
            
            if result != 0:
                return False, f'Cannot connect to {email_host}:{port}'
            
            if verbose:
                self.stdout.write(f'     Email: {email_host}:{port}')
            
            return True, f'SMTP reachable at {email_host}'
        except Exception as e:
            return False, str(e)
