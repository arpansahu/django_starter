"""
Management Command: import_data

Imports data from various sources (CSV, JSON, API).
Demonstrates file handling, progress reporting, and error handling.
"""
import json
import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from commands_app.models import DataImport, TaskStatus


class Command(BaseCommand):
    help = 'Import data from CSV, JSON, or API sources'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'source',
            type=str,
            help='Path to file or URL to import from',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json', 'auto'],
            default='auto',
            help='Source format (default: auto-detect from extension)',
        )
        parser.add_argument(
            '--model',
            type=str,
            required=True,
            help='Target model name (e.g., auth.User)',
        )
        parser.add_argument(
            '--mapping',
            type=str,
            help='JSON file with field mappings',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=100,
            help='Number of records to process per batch (default: 100)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Validate data without actually importing',
        )
        parser.add_argument(
            '--skip-errors',
            action='store_true',
            help='Continue import even if some records fail',
        )
        parser.add_argument(
            '--update-existing',
            action='store_true',
            help='Update existing records instead of skipping',
        )
    
    def handle(self, *args, **options):
        source = options['source']
        format_type = options['format']
        model_name = options['model']
        dry_run = options['dry_run']
        skip_errors = options['skip_errors']
        batch_size = options['batch_size']
        
        # Auto-detect format
        if format_type == 'auto':
            format_type = self._detect_format(source)
        
        self.stdout.write(f'📥 Import configuration:')
        self.stdout.write(f'   - Source: {source}')
        self.stdout.write(f'   - Format: {format_type}')
        self.stdout.write(f'   - Target model: {model_name}')
        self.stdout.write(f'   - Dry run: {dry_run}')
        
        # Create import record
        import_record = DataImport.objects.create(
            name=f'Import from {Path(source).name}',
            source_type='file',
            source_path=source,
            status=TaskStatus.RUNNING,
            started_at=timezone.now(),
        )
        
        try:
            # Load data
            if format_type == 'csv':
                data = self._load_csv(source)
            elif format_type == 'json':
                data = self._load_json(source)
            else:
                raise CommandError(f'Unsupported format: {format_type}')
            
            import_record.total_records = len(data)
            import_record.save()
            
            self.stdout.write(f'\n📊 Found {len(data)} records to import')
            
            # Process data
            success_count = 0
            error_count = 0
            errors = []
            
            for i, record in enumerate(data, 1):
                try:
                    if not dry_run:
                        self._import_record(record, model_name)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append(f'Record {i}: {str(e)}')
                    if not skip_errors:
                        raise
                
                import_record.processed_records = i
                import_record.successful_records = success_count
                import_record.failed_records = error_count
                
                # Progress update every batch_size records
                if i % batch_size == 0:
                    import_record.save()
                    self.stdout.write(f'   Processed {i}/{len(data)} records...')
            
            # Final update
            import_record.status = TaskStatus.COMPLETED
            import_record.completed_at = timezone.now()
            import_record.error_log = '\n'.join(errors) if errors else ''
            import_record.result_summary = {
                'total': len(data),
                'successful': success_count,
                'failed': error_count,
            }
            import_record.save()
            
            # Summary
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Import completed: {success_count} successful, {error_count} failed'
            ))
            
            if dry_run:
                self.stdout.write(self.style.WARNING('⚠️  Dry run - no data was actually imported'))
                
        except Exception as e:
            import_record.status = TaskStatus.FAILED
            import_record.completed_at = timezone.now()
            import_record.error_log = str(e)
            import_record.save()
            raise CommandError(f'Import failed: {e}')
    
    def _detect_format(self, source: str) -> str:
        """Auto-detect format from file extension"""
        path = Path(source)
        ext = path.suffix.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext in ['.json', '.jsonl']:
            return 'json'
        else:
            raise CommandError(f'Cannot auto-detect format for: {source}')
    
    def _load_csv(self, source: str) -> list:
        """Load data from CSV file"""
        data = []
        with open(source, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    def _load_json(self, source: str) -> list:
        """Load data from JSON file"""
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'data' in data:
            return data['data']
        else:
            return [data]
    
    def _import_record(self, record: dict, model_name: str):
        """Import a single record into the specified model"""
        # This is a placeholder - in a real implementation,
        # you would dynamically get the model and create instances
        from django.apps import apps
        
        try:
            app_label, model = model_name.split('.')
            Model = apps.get_model(app_label, model)
        except (ValueError, LookupError) as e:
            raise CommandError(f'Invalid model: {model_name}')
        
        # Create the record
        with transaction.atomic():
            Model.objects.create(**record)
