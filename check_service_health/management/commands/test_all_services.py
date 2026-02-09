# check_service_health/management/commands/test_all_services.py

from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.conf import settings
from io import StringIO


class Command(BaseCommand):
    help = 'Run all service health checks for the Django Starter application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Show detailed output for each service'
        )
        parser.add_argument(
            '--skip',
            nargs='+',
            type=str,
            metavar='SERVICE',
            help='Skip specific services (e.g., --skip kafka rabbitmq)'
        )
        parser.add_argument(
            '--only',
            nargs='+',
            type=str,
            metavar='SERVICE',
            help='Only check specific services (e.g., --only db cache)'
        )

    def handle(self, *args, **options):
        verbose = options.get('detailed', False)
        skip_services = options.get('skip') or []
        only_services = options.get('only')
        
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS(
            '   🏥 DJANGO STARTER - SERVICE HEALTH CHECK'
        ))
        self.stdout.write('='*70 + '\n')
        
        # Define all available services
        all_services = [
            ('db', 'test_db', 'Database (PostgreSQL)', True),
            ('cache', 'test_cache', 'Cache (Redis)', True),
            ('celery', 'test_celery', 'Celery Workers', True),
            ('storage', 'test_storage', 'Storage (MinIO/S3)', True),
            ('flower', 'test_flower', 'Flower Monitoring', False),
            ('elasticsearch', 'test_elasticsearch', 'Elasticsearch', self._is_elasticsearch_configured()),
            ('kafka', 'test_kafka', 'Apache Kafka', self._is_kafka_configured()),
            ('rabbitmq', 'test_rabbitmq', 'RabbitMQ', self._is_rabbitmq_configured()),
            ('email', 'test_email', 'Email Service (MailJet)', self._is_email_configured()),
            ('harbor', 'test_harbor', 'Harbor Registry', self._is_harbor_configured()),
        ]
        
        # Filter services based on arguments
        services_to_check = []
        for key, command, name, is_configured in all_services:
            if only_services:
                if key in only_services:
                    services_to_check.append((key, command, name, is_configured))
            elif key not in skip_services:
                services_to_check.append((key, command, name, is_configured))
        
        results = {}
        
        for key, command, service_name, is_configured in services_to_check:
            self.stdout.write(f'{"-"*70}')
            
            if not is_configured:
                self.stdout.write(self.style.WARNING(f'⏭️  {service_name}: SKIPPED (not configured)'))
                results[service_name] = '⏭️  SKIPPED'
                continue
            
            self.stdout.write(self.style.HTTP_INFO(f'🔍 Testing: {service_name}'))
            self.stdout.write(f'{"-"*70}')
            
            out = StringIO()
            err = StringIO()
            
            try:
                # Build command arguments
                cmd_kwargs = {'stdout': out, 'stderr': err}
                if verbose:
                    cmd_kwargs['verbosity'] = 2
                
                call_command(command, **cmd_kwargs)
                output = out.getvalue()
                error = err.getvalue()
                
                if error:
                    self.stdout.write(self.style.ERROR(error))
                    results[service_name] = '❌ FAILED'
                elif 'ERROR' in output.upper() or 'FAILED' in output.upper() or '❌' in output:
                    self.stdout.write(output)
                    results[service_name] = '❌ FAILED'
                elif '⚠️' in output or 'WARNING' in output.upper():
                    self.stdout.write(output)
                    results[service_name] = '⚠️  WARNING'
                else:
                    self.stdout.write(output)
                    results[service_name] = '✅ PASSED'
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error running {command}: {e}'))
                results[service_name] = '❌ FAILED'
            
            self.stdout.write('')
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('   📊 HEALTH CHECK SUMMARY'))
        self.stdout.write('='*70)
        
        for service_name, status in results.items():
            if '✅' in status:
                style = self.style.SUCCESS
            elif '⚠️' in status:
                style = self.style.WARNING
            elif '⏭️' in status:
                style = self.style.HTTP_INFO
            else:
                style = self.style.ERROR
            
            self.stdout.write(style(f'  {service_name:.<45} {status}'))
        
        self.stdout.write('='*70)
        
        # Overall status
        failed_count = sum(1 for s in results.values() if '❌' in s)
        warning_count = sum(1 for s in results.values() if '⚠️' in s)
        passed_count = sum(1 for s in results.values() if '✅' in s)
        skipped_count = sum(1 for s in results.values() if '⏭️' in s)
        
        self.stdout.write('')
        self.stdout.write(f'  Passed:  {passed_count}')
        self.stdout.write(f'  Warning: {warning_count}')
        self.stdout.write(f'  Failed:  {failed_count}')
        self.stdout.write(f'  Skipped: {skipped_count}')
        self.stdout.write('')
        
        if failed_count == 0 and warning_count == 0:
            self.stdout.write(self.style.SUCCESS('🎉 All services are healthy!\n'))
            return
        elif failed_count == 0:
            self.stdout.write(self.style.WARNING(
                f'⚠️  All critical services are up, {warning_count} warning(s)\n'
            ))
            return
        else:
            self.stdout.write(self.style.ERROR(
                f'❌ {failed_count} service(s) failed health check!\n'
            ))
            raise CommandError(f'{failed_count} service(s) failed health check')
    
    def _is_elasticsearch_configured(self):
        """Check if Elasticsearch is configured"""
        return bool(getattr(settings, 'ELASTICSEARCH_HOST', None))
    
    def _is_kafka_configured(self):
        """Check if Kafka is configured"""
        return bool(getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', None))
    
    def _is_rabbitmq_configured(self):
        """Check if RabbitMQ is configured"""
        return bool(getattr(settings, 'RABBITMQ_HOST', None))
    
    def _is_email_configured(self):
        """Check if Email is configured"""
        return bool(getattr(settings, 'MAIL_JET_API_KEY', None))
    
    def _is_harbor_configured(self):
        """Check if Harbor is configured"""
        return bool(getattr(settings, 'HARBOR_URL', None))
