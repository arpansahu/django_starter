from django.contrib import admin
from .models import Event, EventAggregate


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'event_type', 'kafka_topic', 
        'kafka_partition', 'kafka_offset', 'event_timestamp'
    ]
    list_filter = ['event_type', 'kafka_topic', 'event_timestamp']
    search_fields = ['user__email', 'user__username', 'event_type', 'session_id', 'event_id']
    readonly_fields = [
        'event_timestamp', 'processed_at', 'kafka_topic', 'kafka_partition', 
        'kafka_offset', 'event_id'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_id', 'event_type', 'event_name', 'user', 'source')
        }),
        ('Event Data', {
            'fields': ('event_data', 'metadata')
        }),
        ('Session Information', {
            'fields': ('session_id', 'ip_address', 'user_agent', 'duration_ms'),
            'classes': ('collapse',)
        }),
        ('Kafka Metadata', {
            'fields': ('kafka_topic', 'kafka_partition', 'kafka_offset'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('event_timestamp', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('user')


@admin.register(EventAggregate)
class EventAggregateAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'event_type', 'aggregation_type', 
        'time_bucket', 'event_count', 'unique_users'
    ]
    list_filter = ['event_type', 'aggregation_type', 'time_bucket']
    search_fields = ['event_type']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('event_type', 'aggregation_type')
        }),
        ('Period', {
            'fields': ('time_bucket',)
        }),
        ('Metrics', {
            'fields': ('event_count', 'unique_users', 'avg_duration_ms')
        }),
        ('Analytics Data', {
            'fields': ('stats',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
