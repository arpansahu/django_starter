"""
Models for Commands App - Task and Job tracking for management commands
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class TaskStatus(models.TextChoices):
    """Task status choices"""
    PENDING = 'pending', 'Pending'
    RUNNING = 'running', 'Running'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'


class TaskPriority(models.TextChoices):
    """Task priority choices"""
    LOW = 'low', 'Low'
    MEDIUM = 'medium', 'Medium'
    HIGH = 'high', 'High'
    CRITICAL = 'critical', 'Critical'


class ScheduledTask(models.Model):
    """Model for scheduled tasks/jobs"""
    name = models.CharField(max_length=255)
    command = models.CharField(max_length=255, help_text="Management command to run")
    arguments = models.JSONField(default=dict, blank=True, help_text="Command arguments as JSON")
    schedule = models.CharField(max_length=100, help_text="Cron-like schedule expression")
    is_active = models.BooleanField(default=True)
    priority = models.CharField(max_length=20, choices=TaskPriority.choices, default=TaskPriority.MEDIUM)
    
    # Execution tracking
    last_run = models.DateTimeField(null=True, blank=True)
    next_run = models.DateTimeField(null=True, blank=True)
    run_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='scheduled_tasks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-priority', 'next_run']
        verbose_name = 'Scheduled Task'
        verbose_name_plural = 'Scheduled Tasks'
    
    def __str__(self):
        return f"{self.name} ({self.command})"
    
    def mark_run(self):
        """Mark the task as having been run"""
        self.last_run = timezone.now()
        self.run_count += 1
        self.save(update_fields=['last_run', 'run_count'])


class TaskExecution(models.Model):
    """Model for tracking task execution history"""
    task = models.ForeignKey(ScheduledTask, on_delete=models.CASCADE, related_name='executions')
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    
    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Results
    output = models.TextField(blank=True, help_text="Command output")
    error_message = models.TextField(blank=True, help_text="Error message if failed")
    exit_code = models.IntegerField(null=True, blank=True)
    
    # Context
    triggered_by = models.CharField(max_length=50, default='scheduler')  # scheduler, manual, api
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Task Execution'
        verbose_name_plural = 'Task Executions'
    
    def __str__(self):
        return f"{self.task.name} - {self.status} ({self.started_at})"
    
    def mark_completed(self, output='', exit_code=0):
        """Mark execution as completed"""
        self.status = TaskStatus.COMPLETED
        self.completed_at = timezone.now()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.output = output
        self.exit_code = exit_code
        self.save()
    
    def mark_failed(self, error_message, exit_code=1):
        """Mark execution as failed"""
        self.status = TaskStatus.FAILED
        self.completed_at = timezone.now()
        self.duration_seconds = (self.completed_at - self.started_at).total_seconds()
        self.error_message = error_message
        self.exit_code = exit_code
        self.save()


class CommandLog(models.Model):
    """Model for logging all management command executions"""
    command_name = models.CharField(max_length=255)
    arguments = models.JSONField(default=dict, blank=True)
    
    # Execution details
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Results
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.RUNNING)
    output = models.TextField(blank=True)
    error_output = models.TextField(blank=True)
    exit_code = models.IntegerField(null=True, blank=True)
    
    # Context
    executed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    hostname = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Command Log'
        verbose_name_plural = 'Command Logs'
    
    def __str__(self):
        return f"{self.command_name} ({self.started_at})"


class SystemMetric(models.Model):
    """Model for storing system metrics collected by management commands"""
    name = models.CharField(max_length=100)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Categorization
    category = models.CharField(max_length=50, default='system')  # system, database, cache, etc.
    tags = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'System Metric'
        verbose_name_plural = 'System Metrics'
        indexes = [
            models.Index(fields=['name', '-timestamp']),
            models.Index(fields=['category', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unit}"


class DataImport(models.Model):
    """Model for tracking data import operations"""
    name = models.CharField(max_length=255)
    source_type = models.CharField(max_length=50)  # file, api, database
    source_path = models.CharField(max_length=500)
    
    # Status
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_records = models.PositiveIntegerField(default=0)
    processed_records = models.PositiveIntegerField(default=0)
    successful_records = models.PositiveIntegerField(default=0)
    failed_records = models.PositiveIntegerField(default=0)
    
    # Results
    error_log = models.TextField(blank=True)
    result_summary = models.JSONField(default=dict, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Data Import'
        verbose_name_plural = 'Data Imports'
    
    def __str__(self):
        return f"{self.name} - {self.status}"
    
    @property
    def progress_percentage(self):
        if self.total_records == 0:
            return 0
        return (self.processed_records / self.total_records) * 100


class DataExport(models.Model):
    """Model for tracking data export operations"""
    name = models.CharField(max_length=255)
    export_format = models.CharField(max_length=20)  # csv, json, xlsx, xml
    destination_path = models.CharField(max_length=500)
    
    # Query/Filter
    model_name = models.CharField(max_length=100)
    filters = models.JSONField(default=dict, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=TaskStatus.choices, default=TaskStatus.PENDING)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_records = models.PositiveIntegerField(default=0)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)
    
    # Metadata
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Data Export'
        verbose_name_plural = 'Data Exports'
    
    def __str__(self):
        return f"{self.name} ({self.export_format})"
