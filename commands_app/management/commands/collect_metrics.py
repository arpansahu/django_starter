"""
Management Command: collect_metrics

Collects system metrics and stores them in the database.
Demonstrates a command with multiple arguments and options.
"""
import os
import platform
import psutil
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from commands_app.models import SystemMetric, CommandLog


class Command(BaseCommand):
    help = 'Collect system metrics and store them in the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--categories',
            nargs='+',
            default=['cpu', 'memory', 'disk'],
            help='Categories of metrics to collect (cpu, memory, disk, network)',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=1,
            help='Collection interval in seconds (for continuous mode)',
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Run continuously until interrupted',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show metrics without saving to database',
        )
        parser.add_argument(
            '--verbose-output',
            action='store_true',
            help='Show detailed output',
        )
    
    def handle(self, *args, **options):
        categories = options['categories']
        dry_run = options['dry_run']
        verbose = options['verbose_output']
        
        # Log command execution
        log = None
        if not dry_run:
            log = CommandLog.objects.create(
                command_name='collect_metrics',
                arguments={'categories': categories, 'dry_run': dry_run},
                hostname=platform.node(),
            )
        
        try:
            metrics_collected = []
            
            if 'cpu' in categories:
                metrics_collected.extend(self._collect_cpu_metrics(dry_run, verbose))
            
            if 'memory' in categories:
                metrics_collected.extend(self._collect_memory_metrics(dry_run, verbose))
            
            if 'disk' in categories:
                metrics_collected.extend(self._collect_disk_metrics(dry_run, verbose))
            
            if 'network' in categories:
                metrics_collected.extend(self._collect_network_metrics(dry_run, verbose))
            
            # Summary
            self.stdout.write(self.style.SUCCESS(
                f'✅ Collected {len(metrics_collected)} metrics'
            ))
            
            if log:
                log.status = 'completed'
                log.completed_at = timezone.now()
                log.exit_code = 0
                log.output = f'Collected {len(metrics_collected)} metrics'
                log.save()
                
        except Exception as e:
            if log:
                log.status = 'failed'
                log.completed_at = timezone.now()
                log.exit_code = 1
                log.error_output = str(e)
                log.save()
            raise CommandError(f'Failed to collect metrics: {e}')
    
    def _collect_cpu_metrics(self, dry_run: bool, verbose: bool):
        """Collect CPU metrics"""
        metrics = []
        
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        
        if verbose:
            self.stdout.write(f'  CPU Usage: {cpu_percent}%')
            self.stdout.write(f'  CPU Cores: {cpu_count}')
        
        if not dry_run:
            metrics.append(SystemMetric.objects.create(
                name='cpu_usage_percent',
                value=cpu_percent,
                unit='%',
                category='cpu',
            ))
            metrics.append(SystemMetric.objects.create(
                name='cpu_count',
                value=cpu_count,
                unit='cores',
                category='cpu',
            ))
        
        return metrics
    
    def _collect_memory_metrics(self, dry_run: bool, verbose: bool):
        """Collect memory metrics"""
        metrics = []
        
        memory = psutil.virtual_memory()
        
        if verbose:
            self.stdout.write(f'  Memory Used: {memory.percent}%')
            self.stdout.write(f'  Memory Available: {memory.available / (1024**3):.2f} GB')
        
        if not dry_run:
            metrics.append(SystemMetric.objects.create(
                name='memory_usage_percent',
                value=memory.percent,
                unit='%',
                category='memory',
            ))
            metrics.append(SystemMetric.objects.create(
                name='memory_available_gb',
                value=memory.available / (1024**3),
                unit='GB',
                category='memory',
            ))
        
        return metrics
    
    def _collect_disk_metrics(self, dry_run: bool, verbose: bool):
        """Collect disk metrics"""
        metrics = []
        
        disk = psutil.disk_usage('/')
        
        if verbose:
            self.stdout.write(f'  Disk Used: {disk.percent}%')
            self.stdout.write(f'  Disk Free: {disk.free / (1024**3):.2f} GB')
        
        if not dry_run:
            metrics.append(SystemMetric.objects.create(
                name='disk_usage_percent',
                value=disk.percent,
                unit='%',
                category='disk',
            ))
            metrics.append(SystemMetric.objects.create(
                name='disk_free_gb',
                value=disk.free / (1024**3),
                unit='GB',
                category='disk',
            ))
        
        return metrics
    
    def _collect_network_metrics(self, dry_run: bool, verbose: bool):
        """Collect network metrics"""
        metrics = []
        
        net_io = psutil.net_io_counters()
        
        if verbose:
            self.stdout.write(f'  Bytes Sent: {net_io.bytes_sent / (1024**2):.2f} MB')
            self.stdout.write(f'  Bytes Received: {net_io.bytes_recv / (1024**2):.2f} MB')
        
        if not dry_run:
            metrics.append(SystemMetric.objects.create(
                name='network_bytes_sent_mb',
                value=net_io.bytes_sent / (1024**2),
                unit='MB',
                category='network',
            ))
            metrics.append(SystemMetric.objects.create(
                name='network_bytes_recv_mb',
                value=net_io.bytes_recv / (1024**2),
                unit='MB',
                category='network',
            ))
        
        return metrics
