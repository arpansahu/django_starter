"""
Management Command: run_scheduled_tasks

Runs scheduled tasks based on their configuration.
Demonstrates task scheduling and execution management.
"""
import time
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from django.utils import timezone
from django.db import transaction
from commands_app.models import ScheduledTask, TaskExecution, TaskStatus


class Command(BaseCommand):
    help = 'Run scheduled tasks that are due for execution'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--once',
            action='store_true',
            help='Run once and exit (default: run continuously)',
        )
        parser.add_argument(
            '--task-id',
            type=int,
            help='Run a specific task by ID',
        )
        parser.add_argument(
            '--priority',
            type=str,
            choices=['low', 'medium', 'high', 'critical'],
            help='Only run tasks of this priority or higher',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be executed without running',
        )
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Check interval in seconds for continuous mode (default: 60)',
        )
    
    def handle(self, *args, **options):
        once = options['once']
        task_id = options['task_id']
        priority = options['priority']
        dry_run = options['dry_run']
        interval = options['interval']
        
        self.stdout.write(f'🕐 Task Scheduler started')
        self.stdout.write(f'   - Mode: {"once" if once else "continuous"}')
        self.stdout.write(f'   - Dry run: {dry_run}')
        
        if once:
            self._run_due_tasks(task_id, priority, dry_run)
        else:
            self.stdout.write(f'   - Interval: {interval}s')
            self.stdout.write(f'\nPress Ctrl+C to stop\n')
            
            try:
                while True:
                    self._run_due_tasks(task_id, priority, dry_run)
                    time.sleep(interval)
            except KeyboardInterrupt:
                self.stdout.write(self.style.SUCCESS('\n✅ Scheduler stopped'))
    
    def _run_due_tasks(self, task_id, priority, dry_run):
        """Find and run tasks that are due"""
        now = timezone.now()
        
        # Build queryset
        queryset = ScheduledTask.objects.filter(is_active=True)
        
        if task_id:
            queryset = queryset.filter(id=task_id)
        
        if priority:
            priority_order = ['low', 'medium', 'high', 'critical']
            min_priority_index = priority_order.index(priority)
            valid_priorities = priority_order[min_priority_index:]
            queryset = queryset.filter(priority__in=valid_priorities)
        
        # Filter by next_run
        queryset = queryset.filter(
            models.Q(next_run__lte=now) | models.Q(next_run__isnull=True)
        )
        
        tasks = list(queryset)
        
        if not tasks:
            self.stdout.write(f'[{now}] No tasks due')
            return
        
        self.stdout.write(f'\n[{now}] Found {len(tasks)} task(s) due:')
        
        for task in tasks:
            self._execute_task(task, dry_run)
    
    def _execute_task(self, task, dry_run):
        """Execute a single task"""
        self.stdout.write(f'   📋 {task.name} ({task.command})')
        
        if dry_run:
            self.stdout.write(self.style.WARNING(f'      [DRY RUN] Would execute: {task.command}'))
            return
        
        # Create execution record
        execution = TaskExecution.objects.create(
            task=task,
            status=TaskStatus.RUNNING,
            triggered_by='scheduler',
        )
        
        try:
            # Execute the command
            from io import StringIO
            output = StringIO()
            
            # Parse arguments
            args = task.arguments.get('args', [])
            kwargs = task.arguments.get('kwargs', {})
            
            call_command(
                task.command,
                *args,
                stdout=output,
                **kwargs
            )
            
            # Mark as completed
            execution.mark_completed(output=output.getvalue())
            task.mark_run()
            
            self.stdout.write(self.style.SUCCESS(f'      ✅ Completed'))
            
        except Exception as e:
            execution.mark_failed(error_message=str(e))
            self.stdout.write(self.style.ERROR(f'      ❌ Failed: {e}'))


# Need to import models for the Q object
from django.db import models
