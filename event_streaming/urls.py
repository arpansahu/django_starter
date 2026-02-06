from django.urls import path
from . import views

urlpatterns = [
    path('test-connection/', views.test_kafka_connection, name='test_kafka_connection'),
    path('publish/', views.publish_event, name='publish_event'),
    path('dashboard/', views.event_dashboard, name='event_dashboard'),
    path('analytics/', views.event_analytics, name='event_analytics'),
]
