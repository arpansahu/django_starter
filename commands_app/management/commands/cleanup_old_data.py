"""
Management Command: cleanup_old_data

Cleans up old data from various tables based on retention policies.
Demonstrates a command with date/time handling and batch operations.
"""
from datetime import timedelta
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from commands_app.models import CommandLog, TaskExecution, SystemMetric


class Command(BaseCommand):
    help = 'Clean up old data based on retention policies'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Delete data older than this many days (default: 30)',
        )
        parser.add_argument(
            '--model',
            type=str,
            choices=['all', 'logs', 'executions', 'metrics'],
            default='all',
            help='Which model to clean up (default: all)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to delete per batch (default: 1000)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )
        parser.add_argument(
            '--no-confirm',
            action='store_true',
            help='Skip confirmation prompt',
        )
    
    def handle(self, *args, **options):
        days = options['days']
        model = options['model']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        no_confirm = options['no_confirm']
        
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'🗑️  Cleanup configuration:')
        self.stdout.write(f'   - Cutoff date: {cutoff_date}')
        self.stdout.write(f'   - Model: {model}')
        self.stdout.write(f'   - Batch size: {batch_size}')
        self.stdout.write(f'   - Dry run: {dry_run}')
        
        # Count records to delete
        counts = self._count_records(model, cutoff_date)
        total_count = sum(counts.values())
        
        if total_count == 0:
            self.stdout.write(self.style.SUCCESS('✅ No old data found to clean up'))
            return
        
        self.stdout.write(f'\n📊 Records to delete:')
        for name, count in counts.items():
            self.stdout.write(f'   - {name}: {count}')
        self.stdout.write(f'   - Total: {total_count}')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n⚠️  Dry run mode - no data was deleted'))
            return
        
        # Confirm deletion
        if not no_confirm:
            confirm = input(f'\n⚠️  Delete {total_count} records? [y/N]: ')
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Cancelled'))
                return
        
        # Perform deletion
        deleted = self._delete_records(model, cutoff_date, batch_size)
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Deleted {sum(deleted.values())} records'))
        for name, count in deleted.items():
            self.stdout.write(f'   - {name}: {count}')
    
    def _count_records(self, model: str, cutoff_date) -> dict:
        """Count records to be deleted"""
        counts = {}
        
        if model in ['all', 'logs']:
            counts['CommandLog'] = CommandLog.objects.filter(
                started_at__lt=cutoff_date
            ).count()
        
        if model in ['all', 'executions']:
            counts['TaskExecution'] = TaskExecution.objects.filter(
                started_at__lt=cutoff_date
            ).count()
        
        if model in ['all', 'metrics']:
            counts['SystemMetric'] = SystemMetric.objects.filter(
                timestamp__lt=cutoff_date
            ).count()
        
        return counts
    
    def _delete_records(self, model: str, cutoff_date, batch_size: int) -> dict:
        """Delete records in batches"""
        deleted = {}
        
        if model in ['all', 'logs']:
            deleted['CommandLog'] = self._batch_delete(
                CommandLog.objects.filter(started_at__lt=cutoff_date),
                batch_size
            )
        
        if model in ['all', 'executions']:
            deleted['TaskExecution'] = self._batch_delete(
                TaskExecution.objects.filter(started_at__lt=cutoff_date),
                batch_size
            )
        
        if model in ['all', 'metrics']:
            deleted['SystemMetric'] = self._batch_delete(
                SystemMetric.objects.filter(timestamp__lt=cutoff_date),
                batch_size
            )
        
        return deleted
    
    def _batch_delete(self, queryset, batch_size: int) -> int:
        """Delete records in batches to avoid memory issues"""
        total_deleted = 0
        
        while True:
            # Get batch of IDs to delete
            ids = list(queryset.values_list('id', flat=True)[:batch_size])
            if not ids:
                break
            
            # Delete batch
            with transaction.atomic():
                deleted, _ = queryset.filter(id__in=ids).delete()
                total_deleted += deleted
            
            self.stdout.write(f'   Deleted batch: {deleted} records')
        
        return total_deleted
