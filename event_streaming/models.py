from django.db import models
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class Event(models.Model):
    """Store event metadata for Kafka streams"""
    
    EVENT_TYPES = [
        ('user_action', 'User Action'),
        ('system_event', 'System Event'),
        ('api_call', 'API Call'),
        ('page_view', 'Page View'),
        ('file_upload', 'File Upload'),
        ('task_execution', 'Task Execution'),
        ('error', 'Error Event'),
    ]
    
    # Event identification
    event_id = models.CharField(max_length=100, unique=True, db_index=True)
    event_type = models.CharField(max_length=50, choices=EVENT_TYPES, db_index=True)
    event_name = models.CharField(max_length=255)
    
    # Event source
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    source = models.CharField(max_length=100)  # e.g., 'web', 'mobile', 'api'
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, null=True, blank=True)
    
    # Event data
    event_data = models.JSONField(default=dict)  # Flexible storage for any event-specific data
    metadata = models.JSONField(default=dict)  # Additional metadata
    
    # Kafka metadata
    kafka_topic = models.CharField(max_length=100, db_index=True)
    kafka_partition = models.IntegerField(null=True, blank=True)
    kafka_offset = models.BigIntegerField(null=True, blank=True)
    
    # Timestamps
    event_timestamp = models.DateTimeField(db_index=True)
    processed_at = models.DateTimeField(auto_now_add=True)
    
    # Analytics fields
    session_id = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    duration_ms = models.IntegerField(null=True, blank=True)  # For tracking action duration
    
    class Meta:
        ordering = ['-event_timestamp']
        indexes = [
            models.Index(fields=['event_type', 'event_timestamp']),
            models.Index(fields=['user', 'event_timestamp']),
            models.Index(fields=['kafka_topic', 'event_timestamp']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.event_name} at {self.event_timestamp}"
    
    def get_event_data_display(self):
        """Pretty print event data"""
        return json.dumps(self.event_data, indent=2)


class EventAggregate(models.Model):
    """Store aggregated analytics from Kafka streams"""
    
    AGGREGATION_TYPES = [
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
    ]
    
    aggregation_type = models.CharField(max_length=20, choices=AGGREGATION_TYPES)
    event_type = models.CharField(max_length=50)
    time_bucket = models.DateTimeField(db_index=True)
    
    # Metrics
    event_count = models.IntegerField(default=0)
    unique_users = models.IntegerField(default=0)
    avg_duration_ms = models.FloatField(null=True, blank=True)
    
    # Additional stats
    stats = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-time_bucket']
        unique_together = ['aggregation_type', 'event_type', 'time_bucket']
        indexes = [
            models.Index(fields=['event_type', 'time_bucket']),
        ]
    
    def __str__(self):
        return f"{self.event_type} - {self.aggregation_type} - {self.time_bucket}"

