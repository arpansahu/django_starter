from django.db import models
from user_account.models import Account


class Notification(models.Model):
    """Notification model for RabbitMQ message tracking"""
    
    TYPE_CHOICES = [
        ('info', 'Information'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('success', 'Success'),
        ('alert', 'Alert'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
        ('dead_letter', 'Dead Letter'),
    ]
    
    # Priority mapping for RabbitMQ (0-9, where 9 is highest)
    PRIORITY_MAPPING = {
        'low': 3,
        'medium': 5,
        'high': 7,
        'urgent': 9,
    }
    
    user = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='info')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)
    error_message = models.TextField(blank=True, null=True)
    
    # RabbitMQ specific fields
    message_id = models.CharField(max_length=255, blank=True, null=True)
    queue_name = models.CharField(max_length=255, blank=True, null=True)
    routing_key = models.CharField(max_length=255, blank=True, null=True)
    exchange_name = models.CharField(max_length=255, blank=True, null=True, default='notifications_exchange')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)
    failed_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['notification_type', 'priority']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type.upper()}: {self.title} - {self.status}"
