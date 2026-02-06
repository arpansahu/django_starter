from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'notification_type', 'priority', 
        'status', 'retry_count', 'created_at'
    ]
    list_filter = ['status', 'priority', 'notification_type', 'created_at']
    search_fields = ['user__email', 'user__username', 'title', 'message']
    readonly_fields = [
        'created_at', 'updated_at', 'sent_at', 'delivered_at', 
        'failed_at', 'message_id', 'routing_key'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'notification_type', 'priority', 'title', 'message')
        }),
        ('Status', {
            'fields': ('status', 'retry_count', 'max_retries', 'error_message')
        }),
        ('RabbitMQ Metadata', {
            'fields': ('message_id', 'queue_name', 'routing_key', 'exchange_name'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'sent_at', 'delivered_at', 'failed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')
