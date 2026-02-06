from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Count, Avg
from django.utils import timezone
from .kafka_service import kafka_producer
from .models import Event, EventAggregate
import json
import uuid


def test_kafka_connection(request):
    """Test Kafka connectivity"""
    result = kafka_producer.test_connection()
    return JsonResponse(result)


@login_required
@require_http_methods(["GET", "POST"])
def publish_event(request):
    """Publish a test event to Kafka"""
    if request.method == 'POST':
        event_type = request.POST.get('event_type', 'page_view')
        event_name = request.POST.get('event_name', 'Test Event')
        event_data_str = request.POST.get('event_data', '{}')
        
        try:
            event_data = json.loads(event_data_str)
        except json.JSONDecodeError:
            event_data = {'raw': event_data_str}
        
        # Add metadata
        event_data.update({
            'user_id': request.user.id,
            'username': request.user.username,
        })
        
        # Prepare event for Kafka
        kafka_message = {
            'event_id': str(uuid.uuid4()),
            'event_type': event_type,
            'event_name': event_name,
            'event_data': event_data,
            'user_id': request.user.id,
            'source': 'web',
            'session_id': request.session.session_key,
            'ip_address': request.META.get('REMOTE_ADDR'),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
            'event_timestamp': timezone.now().isoformat()
        }
        
        # Send to Kafka
        topic = f'events.{event_type}'
        success = kafka_producer.send_message(
            topic=topic,
            message=kafka_message,
            key=str(request.user.id)
        )
        
        # Create event in database (save regardless of Kafka success)
        Event.objects.create(
            event_id=kafka_message['event_id'],
            event_type=event_type,
            event_name=event_name,
            user=request.user,
            source='web',
            event_data=event_data,
            session_id=request.session.session_key,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
            kafka_topic=topic,
            event_timestamp=timezone.now()
        )
        
        if success:
            messages.success(request, 'Event published to Kafka and saved to database!')
        else:
            messages.warning(request, 'Event saved to database, but Kafka is currently unavailable.')
        
        return redirect('publish_event')
    
    # GET request - show form and recent events
    recent_events = Event.objects.filter(user=request.user).order_by('-event_timestamp')[:10]
    
    context = {
        'recent_events': recent_events,
        'event_type_choices': Event.EVENT_TYPES
    }
    
    return render(request, 'event_streaming/publish_event.html', context)


@login_required
def event_dashboard(request):
    """Dashboard showing event statistics"""
    user_events = Event.objects.filter(user=request.user)
    
    # Overall stats
    stats = {
        'total_events': user_events.count(),
        'unique_sessions': user_events.values('session_id').distinct().count(),
    }
    
    # Events by type
    events_by_type = user_events.values('event_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Recent events
    recent_events = user_events.order_by('-event_timestamp')[:20]
    
    context = {
        'stats': stats,
        'events_by_type': events_by_type,
        'recent_events': recent_events
    }
    
    return render(request, 'event_streaming/dashboard.html', context)


@login_required
def event_analytics(request):
    """Analytics dashboard with aggregated data"""
    all_aggregates = EventAggregate.objects.all()
    
    # Daily aggregates
    daily_aggregates = all_aggregates.filter(
        aggregation_type='daily'
    ).order_by('-time_bucket')[:30]
    
    # Hourly aggregates for today
    hourly_aggregates = all_aggregates.filter(
        aggregation_type='hourly'
    ).order_by('-time_bucket')[:24]
    
    context = {
        'daily_aggregates': daily_aggregates,
        'hourly_aggregates': hourly_aggregates
    }
    
    return render(request, 'event_streaming/analytics.html', context)
