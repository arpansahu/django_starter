"""
URL Configuration for Commands App
"""
from django.urls import path
from . import views

app_name = 'commands_app'

urlpatterns = [
    # Dashboard
    path('', views.CommandsDashboardView.as_view(), name='dashboard'),
    
    # Scheduled Tasks
    path('tasks/', views.ScheduledTaskListView.as_view(), name='task_list'),
    path('tasks/create/', views.ScheduledTaskCreateView.as_view(), name='task_create'),
    path('tasks/<int:pk>/', views.ScheduledTaskDetailView.as_view(), name='task_detail'),
    path('tasks/<int:pk>/edit/', views.ScheduledTaskUpdateView.as_view(), name='task_edit'),
    path('tasks/<int:pk>/delete/', views.ScheduledTaskDeleteView.as_view(), name='task_delete'),
    
    # Task Executions
    path('executions/', views.TaskExecutionListView.as_view(), name='execution_list'),
    path('executions/<int:pk>/', views.TaskExecutionDetailView.as_view(), name='execution_detail'),
    
    # Command Logs
    path('logs/', views.CommandLogListView.as_view(), name='log_list'),
    path('logs/<int:pk>/', views.CommandLogDetailView.as_view(), name='log_detail'),
    
    # Run Command
    path('run/', views.RunCommandView.as_view(), name='run_command'),
    
    # Metrics
    path('metrics/', views.MetricsDashboardView.as_view(), name='metrics_dashboard'),
    path('metrics/list/', views.MetricsListView.as_view(), name='metrics_list'),
    
    # Data Import/Export
    path('imports/', views.DataImportListView.as_view(), name='import_list'),
    path('imports/<int:pk>/', views.DataImportDetailView.as_view(), name='import_detail'),
    path('exports/', views.DataExportListView.as_view(), name='export_list'),
    path('exports/<int:pk>/', views.DataExportDetailView.as_view(), name='export_detail'),
    
    # API Endpoints
    path('api/tasks/<int:pk>/run/', views.task_run_api, name='api_task_run'),
    path('api/metrics/', views.metrics_api, name='api_metrics'),
]
