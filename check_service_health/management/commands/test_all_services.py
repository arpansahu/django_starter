# check_service_health/management/commands/test_all_services.py

from django.core.management.base import BaseCommand
from django.core.management import call_command
from io import StringIO


class Command(BaseCommand):
    help = 'Run all service health checks'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Starting All Service Health Checks'))
        self.stdout.write(self.style.SUCCESS('='*70))
        
        services = [
            ('test_db', 'Database (PostgreSQL)'),
            ('test_cache', 'Cache (Redis)'),
            ('test_celery', 'Celery Workers'),
            ('test_storage', 'Storage (MinIO/S3)'),
            ('test_flower', 'Flower Monitoring'),
        ]
        
        results = {}
        
        for command, service_name in services:
            self.stdout.write(f'\n{"-"*70}')
            self.stdout.write(self.style.WARNING(f'Testing: {service_name}'))
            self.stdout.write(f'{"-"*70}')
            
            out = StringIO()
            err = StringIO()
            
            try:
                call_command(command, stdout=out, stderr=err)
                output = out.getvalue()
                error = err.getvalue()
                
                if error:
                    self.stdout.write(self.style.ERROR(error))
                    results[service_name] = '❌ FAILED'
                elif 'ERROR' in output.upper() or 'FAILED' in output.upper():
                    self.stdout.write(output)
                    results[service_name] = '⚠️  WARNING'
                else:
                    self.stdout.write(output)
                    results[service_name] = '✅ PASSED'
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error running {command}: {e}'))
                results[service_name] = '❌ FAILED'
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('Health Check Summary'))
        self.stdout.write('='*70)
        
        for service_name, status in results.items():
            if '✅' in status:
                style = self.style.SUCCESS
            elif '⚠️' in status:
                style = self.style.WARNING
            else:
                style = self.style.ERROR
            
            self.stdout.write(style(f'{service_name:.<40} {status}'))
        
        self.stdout.write('='*70)
        
        # Overall status
        failed_count = sum(1 for s in results.values() if '❌' in s)
        warning_count = sum(1 for s in results.values() if '⚠️' in s)
        passed_count = sum(1 for s in results.values() if '✅' in s)
        
        if failed_count == 0 and warning_count == 0:
            self.stdout.write(self.style.SUCCESS('\n🎉 All services are healthy!'))
        elif failed_count == 0:
            self.stdout.write(self.style.WARNING(f'\n⚠️  All critical services are up, {warning_count} warning(s)'))
        else:
            self.stdout.write(self.style.ERROR(f'\n❌ {failed_count} service(s) failed health check!'))
