"""
Management Command: export_data

Exports data to various formats (CSV, JSON, Excel).
Demonstrates QuerySet handling and file generation.
"""
import json
import csv
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.apps import apps
from commands_app.models import DataExport, TaskStatus


class Command(BaseCommand):
    help = 'Export data to CSV, JSON, or Excel formats'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'model',
            type=str,
            help='Model to export (e.g., auth.User)',
        )
        parser.add_argument(
            'destination',
            type=str,
            help='Destination file path',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['csv', 'json', 'auto'],
            default='auto',
            help='Export format (default: auto-detect from extension)',
        )
        parser.add_argument(
            '--fields',
            nargs='+',
            help='Specific fields to export (default: all)',
        )
        parser.add_argument(
            '--filter',
            type=str,
            help='Filter expression as JSON (e.g., {"is_active": true})',
        )
        parser.add_argument(
            '--order-by',
            type=str,
            help='Field to order by (prefix with - for descending)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Maximum number of records to export',
        )
        parser.add_argument(
            '--pretty',
            action='store_true',
            help='Pretty-print JSON output',
        )
    
    def handle(self, *args, **options):
        model_name = options['model']
        destination = options['destination']
        format_type = options['format']
        fields = options['fields']
        filter_expr = options['filter']
        order_by = options['order_by']
        limit = options['limit']
        pretty = options['pretty']
        
        # Auto-detect format
        if format_type == 'auto':
            format_type = self._detect_format(destination)
        
        # Get model
        try:
            app_label, model = model_name.split('.')
            Model = apps.get_model(app_label, model)
        except (ValueError, LookupError) as e:
            raise CommandError(f'Invalid model: {model_name}')
        
        self.stdout.write(f'📤 Export configuration:')
        self.stdout.write(f'   - Model: {model_name}')
        self.stdout.write(f'   - Destination: {destination}')
        self.stdout.write(f'   - Format: {format_type}')
        
        # Create export record
        export_record = DataExport.objects.create(
            name=f'Export {model_name}',
            export_format=format_type,
            destination_path=destination,
            model_name=model_name,
            status=TaskStatus.RUNNING,
            started_at=timezone.now(),
        )
        
        try:
            # Build queryset
            queryset = Model.objects.all()
            
            if filter_expr:
                try:
                    filters = json.loads(filter_expr)
                    queryset = queryset.filter(**filters)
                except json.JSONDecodeError:
                    raise CommandError(f'Invalid filter JSON: {filter_expr}')
            
            if order_by:
                queryset = queryset.order_by(order_by)
            
            if limit:
                queryset = queryset[:limit]
            
            # Determine fields
            if not fields:
                fields = [f.name for f in Model._meta.fields]
            
            # Get data
            data = list(queryset.values(*fields))
            export_record.total_records = len(data)
            
            self.stdout.write(f'\n📊 Exporting {len(data)} records...')
            
            # Export
            if format_type == 'csv':
                self._export_csv(data, destination, fields)
            elif format_type == 'json':
                self._export_json(data, destination, pretty)
            else:
                raise CommandError(f'Unsupported format: {format_type}')
            
            # Get file size
            file_size = Path(destination).stat().st_size
            
            # Update record
            export_record.status = TaskStatus.COMPLETED
            export_record.completed_at = timezone.now()
            export_record.file_size_bytes = file_size
            export_record.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ Exported {len(data)} records to {destination} ({file_size} bytes)'
            ))
            
        except Exception as e:
            export_record.status = TaskStatus.FAILED
            export_record.completed_at = timezone.now()
            export_record.save()
            raise CommandError(f'Export failed: {e}')
    
    def _detect_format(self, destination: str) -> str:
        """Auto-detect format from file extension"""
        path = Path(destination)
        ext = path.suffix.lower()
        
        if ext == '.csv':
            return 'csv'
        elif ext == '.json':
            return 'json'
        else:
            raise CommandError(f'Cannot auto-detect format for: {destination}')
    
    def _export_csv(self, data: list, destination: str, fields: list):
        """Export data to CSV"""
        with open(destination, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            writer.writerows(data)
    
    def _export_json(self, data: list, destination: str, pretty: bool):
        """Export data to JSON"""
        # Convert datetime objects to strings
        def json_serializer(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            raise TypeError(f'Object of type {type(obj)} is not JSON serializable')
        
        with open(destination, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, default=json_serializer)
            else:
                json.dump(data, f, default=json_serializer)
