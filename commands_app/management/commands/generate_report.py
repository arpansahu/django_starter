"""
Management Command: generate_report

Generates various reports (PDF, CSV, HTML) from data.
Demonstrates complex data aggregation and file generation.
"""
import json
from datetime import datetime, timedelta
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db.models import Count, Avg, Sum, Min, Max
from commands_app.models import (
    ScheduledTask, TaskExecution, CommandLog, 
    SystemMetric, DataImport, DataExport, TaskStatus
)


class Command(BaseCommand):
    help = 'Generate reports from command execution data'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--report-type',
            type=str,
            required=True,
            choices=['summary', 'execution', 'metrics', 'imports', 'full'],
            help='Type of report to generate',
        )
        parser.add_argument(
            '--format',
            type=str,
            choices=['text', 'json', 'csv', 'html'],
            default='text',
            help='Output format (default: text)',
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path (default: stdout)',
        )
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to include in report (default: 7)',
        )
        parser.add_argument(
            '--detailed',
            action='store_true',
            help='Include detailed breakdowns',
        )
    
    def handle(self, *args, **options):
        report_type = options['report_type']
        output_format = options['format']
        output_file = options['output']
        days = options['days']
        detailed = options['detailed']
        
        # Calculate date range
        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)
        
        self.stdout.write(f'📊 Generating {report_type} report...')
        self.stdout.write(f'   Period: {start_date.date()} to {end_date.date()}')
        
        # Generate report data
        if report_type == 'summary':
            data = self._generate_summary_report(start_date, end_date, detailed)
        elif report_type == 'execution':
            data = self._generate_execution_report(start_date, end_date, detailed)
        elif report_type == 'metrics':
            data = self._generate_metrics_report(start_date, end_date, detailed)
        elif report_type == 'imports':
            data = self._generate_imports_report(start_date, end_date, detailed)
        elif report_type == 'full':
            data = self._generate_full_report(start_date, end_date, detailed)
        
        # Format output
        if output_format == 'json':
            output = json.dumps(data, indent=2, default=str)
        elif output_format == 'csv':
            output = self._format_csv(data)
        elif output_format == 'html':
            output = self._format_html(data, report_type)
        else:
            output = self._format_text(data)
        
        # Write output
        if output_file:
            Path(output_file).write_text(output)
            self.stdout.write(self.style.SUCCESS(f'✅ Report saved to {output_file}'))
        else:
            self.stdout.write(output)
    
    def _generate_summary_report(self, start_date, end_date, detailed):
        """Generate summary statistics"""
        return {
            'report_type': 'summary',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'scheduled_tasks': {
                'total': ScheduledTask.objects.count(),
                'active': ScheduledTask.objects.filter(is_active=True).count(),
            },
            'executions': {
                'total': TaskExecution.objects.filter(
                    started_at__range=(start_date, end_date)
                ).count(),
                'by_status': dict(TaskExecution.objects.filter(
                    started_at__range=(start_date, end_date)
                ).values('status').annotate(count=Count('id')).values_list('status', 'count')),
            },
            'command_logs': {
                'total': CommandLog.objects.filter(
                    started_at__range=(start_date, end_date)
                ).count(),
            },
            'system_metrics': {
                'total': SystemMetric.objects.filter(
                    timestamp__range=(start_date, end_date)
                ).count(),
            },
        }
    
    def _generate_execution_report(self, start_date, end_date, detailed):
        """Generate execution report"""
        executions = TaskExecution.objects.filter(
            started_at__range=(start_date, end_date)
        )
        
        data = {
            'report_type': 'execution',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'statistics': {
                'total': executions.count(),
                'completed': executions.filter(status=TaskStatus.COMPLETED).count(),
                'failed': executions.filter(status=TaskStatus.FAILED).count(),
                'avg_duration': executions.aggregate(avg=Avg('duration_seconds'))['avg'],
                'max_duration': executions.aggregate(max=Max('duration_seconds'))['max'],
            },
        }
        
        if detailed:
            data['by_task'] = list(executions.values('task__name').annotate(
                count=Count('id'),
                avg_duration=Avg('duration_seconds'),
                success_rate=Count('id', filter=models.Q(status=TaskStatus.COMPLETED)) * 100.0 / Count('id'),
            ))
        
        return data
    
    def _generate_metrics_report(self, start_date, end_date, detailed):
        """Generate metrics report"""
        metrics = SystemMetric.objects.filter(
            timestamp__range=(start_date, end_date)
        )
        
        data = {
            'report_type': 'metrics',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'by_category': list(metrics.values('category').annotate(
                count=Count('id'),
            )),
            'by_name': list(metrics.values('name').annotate(
                count=Count('id'),
                avg=Avg('value'),
                min=Min('value'),
                max=Max('value'),
            )),
        }
        
        return data
    
    def _generate_imports_report(self, start_date, end_date, detailed):
        """Generate imports/exports report"""
        imports = DataImport.objects.filter(
            created_at__range=(start_date, end_date)
        )
        exports = DataExport.objects.filter(
            created_at__range=(start_date, end_date)
        )
        
        return {
            'report_type': 'imports',
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'imports': {
                'total': imports.count(),
                'by_status': dict(imports.values('status').annotate(
                    count=Count('id')
                ).values_list('status', 'count')),
                'total_records': imports.aggregate(total=Sum('total_records'))['total'] or 0,
            },
            'exports': {
                'total': exports.count(),
                'by_format': dict(exports.values('export_format').annotate(
                    count=Count('id')
                ).values_list('export_format', 'count')),
            },
        }
    
    def _generate_full_report(self, start_date, end_date, detailed):
        """Generate comprehensive report"""
        return {
            'report_type': 'full',
            'generated_at': timezone.now().isoformat(),
            'summary': self._generate_summary_report(start_date, end_date, detailed),
            'executions': self._generate_execution_report(start_date, end_date, detailed),
            'metrics': self._generate_metrics_report(start_date, end_date, detailed),
            'imports': self._generate_imports_report(start_date, end_date, detailed),
        }
    
    def _format_text(self, data):
        """Format data as text"""
        lines = []
        lines.append('=' * 60)
        lines.append(f'Report Type: {data.get("report_type", "unknown").upper()}')
        lines.append('=' * 60)
        
        def format_dict(d, indent=0):
            for key, value in d.items():
                if isinstance(value, dict):
                    lines.append(' ' * indent + f'{key}:')
                    format_dict(value, indent + 2)
                elif isinstance(value, list):
                    lines.append(' ' * indent + f'{key}: [{len(value)} items]')
                else:
                    lines.append(' ' * indent + f'{key}: {value}')
        
        format_dict(data)
        return '\n'.join(lines)
    
    def _format_csv(self, data):
        """Format data as CSV"""
        # Flatten data for CSV
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        def flatten(obj, prefix=''):
            items = []
            if isinstance(obj, dict):
                for k, v in obj.items():
                    items.extend(flatten(v, f'{prefix}{k}_' if prefix else f'{k}_'))
            elif isinstance(obj, list):
                items.append((prefix[:-1], str(obj)))
            else:
                items.append((prefix[:-1], obj))
            return items
        
        rows = flatten(data)
        for key, value in rows:
            writer.writerow([key, value])
        
        return output.getvalue()
    
    def _format_html(self, data, report_type):
        """Format data as HTML"""
        html = f'''<!DOCTYPE html>
<html>
<head>
    <title>{report_type.title()} Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>{report_type.title()} Report</h1>
    <pre>{json.dumps(data, indent=2, default=str)}</pre>
</body>
</html>'''
        return html


# Import models for Q lookups
from django.db import models
