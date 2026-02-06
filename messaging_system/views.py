from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .rabbitmq_service import rabbitmq_producer
from .models import Notification
import json


def test_rabbitmq_connection(request):
    """Test RabbitMQ connectivity"""
    result = rabbitmq_producer.test_connection()
    return JsonResponse(result)


@login_required
@require_http_methods(["GET", "POST"])
def send_notification(request):
    """Send a test notification via RabbitMQ"""
    if request.method == 'POST':
        notification_type = request.POST.get('notification_type', 'info')
        priority = request.POST.get('priority', 'medium')
        title = request.POST.get('title', 'Test Notification')
        message = request.POST.get('message', 'This is a test notification')
        
        # Create notification in database
        notification = Notification.objects.create(
            user=request.user,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            status='pending'
        )
        
        # Prepare message for RabbitMQ
        message_data = {
            'notification_id': notification.id,
            'user_id': request.user.id,
            'type': notification_type,
            'priority': priority,
            'title': title,
            'message': message
        }
        
        # Send to RabbitMQ
        exchange_name = 'notifications_exchange'
        queue_name = f'notifications.{priority}'
        routing_key = f'notification.{notification_type}.{priority}'
        
        success = rabbitmq_producer.publish_message(
            exchange=exchange_name,
            routing_key=routing_key,
            message=message_data,
            priority=Notification.PRIORITY_MAPPING.get(priority, 5)
        )
        
        if success:
            notification.status = 'sent'
            notification.queue_name = queue_name
            notification.routing_key = routing_key
            notification.exchange_name = exchange_name
            notification.save()
            messages.success(request, 'Notification sent successfully!')
        else:
            notification.status = 'failed'
            notification.error_message = 'Failed to publish to RabbitMQ'
            notification.save()
            messages.error(request, 'Failed to send notification')
        
        return redirect('send_notification')
    
    # GET request - show form and recent notifications
    recent_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'recent_notifications': recent_notifications,
        'notification_types': Notification.TYPE_CHOICES,
        'priority_choices': Notification.PRIORITY_CHOICES
    }
    
    return render(request, 'messaging_system/send_notification.html', context)


@login_required
def notification_dashboard(request):
    """Dashboard showing notification statistics"""
    user_notifications = Notification.objects.filter(user=request.user)
    
    stats = {
        'total': user_notifications.count(),
        'pending': user_notifications.filter(status='pending').count(),
        'sent': user_notifications.filter(status='sent').count(),
        'delivered': user_notifications.filter(status='delivered').count(),
        'failed': user_notifications.filter(status='failed').count(),
    }
    
    recent_notifications = user_notifications.order_by('-created_at')[:20]
    
    context = {
        'stats': stats,
        'recent_notifications': recent_notifications
    }
    
    return render(request, 'messaging_system/dashboard.html', context)
