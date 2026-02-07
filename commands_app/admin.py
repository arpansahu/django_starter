"""
Admin configuration for Commands App
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ScheduledTask, TaskExecution, CommandLog,
    SystemMetric, DataImport, DataExport
)


@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = ['name', 'command', 'schedule', 'is_active', 'priority', 'last_run', 'run_count']
    list_filter = ['is_active', 'priority', 'command']
    search_fields = ['name', 'command', 'description']
    ordering = ['-priority', 'name']
    readonly_fields = ['created_at', 'updated_at', 'last_run', 'run_count']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'command', 'arguments', 'schedule')
        }),
        ('Status', {
            'fields': ('is_active', 'priority')
        }),
        ('Execution Info', {
            'fields': ('last_run', 'next_run', 'run_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('description', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TaskExecution)
class TaskExecutionAdmin(admin.ModelAdmin):
    list_display = ['task', 'status_badge', 'started_at', 'duration_seconds', 'triggered_by']
    list_filter = ['status', 'triggered_by', 'task']
    search_fields = ['task__name', 'output', 'error_message']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']
    
    def status_badge(self, obj):
        colors = {
            'pending': 'secondary',
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(CommandLog)
class CommandLogAdmin(admin.ModelAdmin):
    list_display = ['command_name', 'status_badge', 'started_at', 'duration_seconds', 'executed_by']
    list_filter = ['status', 'command_name']
    search_fields = ['command_name', 'output', 'error_output']
    ordering = ['-started_at']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']
    
    def status_badge(self, obj):
        colors = {
            'pending': 'secondary',
            'running': 'primary',
            'completed': 'success',
            'failed': 'danger',
            'cancelled': 'warning',
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            color, obj.status.upper()
        )
    status_badge.short_description = 'Status'


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ['name', 'value', 'unit', 'category', 'timestamp']
    list_filter = ['category', 'name']
    search_fields = ['name']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']


@admin.register(DataImport)
class DataImportAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'status', 'progress', 'created_at']
    list_filter = ['status', 'source_type']
    search_fields = ['name', 'source_path']
    ordering = ['-created_at']
    readonly_fields = ['started_at', 'completed_at', 'total_records', 'processed_records']
    
    def progress(self, obj):
        if obj.total_records == 0:
            return '-'
        pct = (obj.processed_records / obj.total_records) * 100
        return format_html(
            '<div class="progress"><div class="progress-bar" style="width: {}%">{:.0f}%</div></div>',
            pct, pct
        )
    progress.short_description = 'Progress'


@admin.register(DataExport)
class DataExportAdmin(admin.ModelAdmin):
    list_display = ['name', 'export_format', 'model_name', 'status', 'total_records', 'created_at']
    list_filter = ['status', 'export_format']
    search_fields = ['name', 'model_name']
    ordering = ['-created_at']
    readonly_fields = ['started_at', 'completed_at', 'total_records', 'file_size_bytes']
