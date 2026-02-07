"""
Views for Commands App - Dashboard and management interfaces
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView,
    TemplateView, FormView
)
from django.views.generic.edit import FormMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.core.management import call_command, get_commands
from django.utils import timezone
from django.db.models import Count, Avg, Q
from io import StringIO
from datetime import timedelta

from .models import (
    ScheduledTask, TaskExecution, CommandLog,
    SystemMetric, DataImport, DataExport, TaskStatus, TaskPriority
)
from .forms import (
    ScheduledTaskForm, RunCommandForm, DataImportForm, DataExportForm
)


# Dashboard Views
class CommandsDashboardView(LoginRequiredMixin, TemplateView):
    """Main dashboard for commands app"""
    template_name = 'commands_app/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get statistics
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        context['stats'] = {
            'scheduled_tasks': ScheduledTask.objects.count(),
            'active_tasks': ScheduledTask.objects.filter(is_active=True).count(),
            'executions_24h': TaskExecution.objects.filter(started_at__gte=last_24h).count(),
            'executions_7d': TaskExecution.objects.filter(started_at__gte=last_7d).count(),
            'failed_24h': TaskExecution.objects.filter(
                started_at__gte=last_24h, 
                status=TaskStatus.FAILED
            ).count(),
            'commands_24h': CommandLog.objects.filter(started_at__gte=last_24h).count(),
            'metrics_count': SystemMetric.objects.filter(timestamp__gte=last_24h).count(),
        }
        
        # Recent executions
        context['recent_executions'] = TaskExecution.objects.select_related('task')[:10]
        
        # Recent command logs
        context['recent_commands'] = CommandLog.objects.all()[:10]
        
        # Available commands
        context['available_commands'] = sorted(get_commands().keys())
        
        return context


# Scheduled Task Views
class ScheduledTaskListView(LoginRequiredMixin, ListView):
    """List all scheduled tasks"""
    model = ScheduledTask
    template_name = 'commands_app/task_list.html'
    context_object_name = 'tasks'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status == 'active':
            queryset = queryset.filter(is_active=True)
        elif status == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        # Filter by priority
        priority = self.request.GET.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Search
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(command__icontains=search)
            )
        
        return queryset


class ScheduledTaskDetailView(LoginRequiredMixin, DetailView):
    """View details of a scheduled task"""
    model = ScheduledTask
    template_name = 'commands_app/task_detail.html'
    context_object_name = 'task'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent executions for this task
        context['executions'] = self.object.executions.all()[:20]
        
        # Calculate statistics
        executions = self.object.executions.all()
        context['execution_stats'] = {
            'total': executions.count(),
            'completed': executions.filter(status=TaskStatus.COMPLETED).count(),
            'failed': executions.filter(status=TaskStatus.FAILED).count(),
            'avg_duration': executions.aggregate(avg=Avg('duration_seconds'))['avg'],
        }
        
        return context


class ScheduledTaskCreateView(LoginRequiredMixin, CreateView):
    """Create a new scheduled task"""
    model = ScheduledTask
    form_class = ScheduledTaskForm
    template_name = 'commands_app/task_form.html'
    success_url = reverse_lazy('commands_app:task_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Task created successfully!')
        return super().form_valid(form)


class ScheduledTaskUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing scheduled task"""
    model = ScheduledTask
    form_class = ScheduledTaskForm
    template_name = 'commands_app/task_form.html'
    
    def get_success_url(self):
        return reverse_lazy('commands_app:task_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Task updated successfully!')
        return super().form_valid(form)


class ScheduledTaskDeleteView(LoginRequiredMixin, DeleteView):
    """Delete a scheduled task"""
    model = ScheduledTask
    template_name = 'commands_app/task_confirm_delete.html'
    success_url = reverse_lazy('commands_app:task_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Task deleted successfully!')
        return super().delete(request, *args, **kwargs)


# Task Execution Views
class TaskExecutionListView(LoginRequiredMixin, ListView):
    """List all task executions"""
    model = TaskExecution
    template_name = 'commands_app/execution_list.html'
    context_object_name = 'executions'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('task', 'executed_by')
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by task
        task_id = self.request.GET.get('task')
        if task_id:
            queryset = queryset.filter(task_id=task_id)
        
        return queryset


class TaskExecutionDetailView(LoginRequiredMixin, DetailView):
    """View details of a task execution"""
    model = TaskExecution
    template_name = 'commands_app/execution_detail.html'
    context_object_name = 'execution'


# Command Log Views
class CommandLogListView(LoginRequiredMixin, ListView):
    """List all command logs"""
    model = CommandLog
    template_name = 'commands_app/log_list.html'
    context_object_name = 'logs'
    paginate_by = 50
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        
        # Filter by command
        command = self.request.GET.get('command')
        if command:
            queryset = queryset.filter(command_name__icontains=command)
        
        return queryset


class CommandLogDetailView(LoginRequiredMixin, DetailView):
    """View details of a command log"""
    model = CommandLog
    template_name = 'commands_app/log_detail.html'
    context_object_name = 'log'


# Run Command Views
class RunCommandView(LoginRequiredMixin, FormView):
    """Run a management command manually"""
    template_name = 'commands_app/run_command.html'
    form_class = RunCommandForm
    success_url = reverse_lazy('commands_app:log_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['available_commands'] = sorted(get_commands().keys())
        return context
    
    def form_valid(self, form):
        command_name = form.cleaned_data['command']
        arguments = form.cleaned_data.get('arguments', {})
        
        # Create log entry
        log = CommandLog.objects.create(
            command_name=command_name,
            arguments=arguments,
            executed_by=self.request.user,
        )
        
        try:
            # Run command
            output = StringIO()
            call_command(command_name, stdout=output, **arguments)
            
            log.status = TaskStatus.COMPLETED
            log.output = output.getvalue()
            log.exit_code = 0
            log.completed_at = timezone.now()
            log.save()
            
            messages.success(self.request, f'Command "{command_name}" executed successfully!')
            
        except Exception as e:
            log.status = TaskStatus.FAILED
            log.error_output = str(e)
            log.exit_code = 1
            log.completed_at = timezone.now()
            log.save()
            
            messages.error(self.request, f'Command failed: {e}')
        
        return super().form_valid(form)


# System Metrics Views
class MetricsDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard for system metrics"""
    template_name = 'commands_app/metrics_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get recent metrics
        now = timezone.now()
        last_hour = now - timedelta(hours=1)
        
        metrics = SystemMetric.objects.filter(timestamp__gte=last_hour)
        
        # Group by category
        context['metrics_by_category'] = {}
        for category in metrics.values_list('category', flat=True).distinct():
            context['metrics_by_category'][category] = metrics.filter(category=category)
        
        # Latest values
        context['latest_metrics'] = {}
        for name in metrics.values_list('name', flat=True).distinct():
            latest = metrics.filter(name=name).order_by('-timestamp').first()
            if latest:
                context['latest_metrics'][name] = latest
        
        return context


class MetricsListView(LoginRequiredMixin, ListView):
    """List system metrics"""
    model = SystemMetric
    template_name = 'commands_app/metrics_list.html'
    context_object_name = 'metrics'
    paginate_by = 100
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by name
        name = self.request.GET.get('name')
        if name:
            queryset = queryset.filter(name=name)
        
        return queryset


# Data Import/Export Views
class DataImportListView(LoginRequiredMixin, ListView):
    """List data imports"""
    model = DataImport
    template_name = 'commands_app/import_list.html'
    context_object_name = 'imports'
    paginate_by = 20


class DataImportDetailView(LoginRequiredMixin, DetailView):
    """View import details"""
    model = DataImport
    template_name = 'commands_app/import_detail.html'
    context_object_name = 'import_record'


class DataExportListView(LoginRequiredMixin, ListView):
    """List data exports"""
    model = DataExport
    template_name = 'commands_app/export_list.html'
    context_object_name = 'exports'
    paginate_by = 20


class DataExportDetailView(LoginRequiredMixin, DetailView):
    """View export details"""
    model = DataExport
    template_name = 'commands_app/export_detail.html'
    context_object_name = 'export_record'


# API Views
def task_run_api(request, pk):
    """API endpoint to run a task manually"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    task = get_object_or_404(ScheduledTask, pk=pk)
    
    # Create execution record
    execution = TaskExecution.objects.create(
        task=task,
        status=TaskStatus.RUNNING,
        triggered_by='manual',
        executed_by=request.user,
    )
    
    try:
        # Run command
        output = StringIO()
        args = task.arguments.get('args', [])
        kwargs = task.arguments.get('kwargs', {})
        
        call_command(task.command, *args, stdout=output, **kwargs)
        
        execution.mark_completed(output=output.getvalue())
        task.mark_run()
        
        return JsonResponse({
            'success': True,
            'execution_id': execution.id,
            'output': output.getvalue(),
        })
        
    except Exception as e:
        execution.mark_failed(error_message=str(e))
        return JsonResponse({
            'success': False,
            'execution_id': execution.id,
            'error': str(e),
        }, status=500)


def metrics_api(request):
    """API endpoint to get latest metrics"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    
    metrics = SystemMetric.objects.filter(timestamp__gte=last_hour)
    
    data = {}
    for name in metrics.values_list('name', flat=True).distinct():
        latest = metrics.filter(name=name).order_by('-timestamp').first()
        if latest:
            data[name] = {
                'value': latest.value,
                'unit': latest.unit,
                'timestamp': latest.timestamp.isoformat(),
            }
    
    return JsonResponse(data)
