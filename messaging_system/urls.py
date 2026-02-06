from django.urls import path
from . import views

urlpatterns = [
    path('test-connection/', views.test_rabbitmq_connection, name='test_rabbitmq_connection'),
    path('send/', views.send_notification, name='send_notification'),
    path('dashboard/', views.notification_dashboard, name='notification_dashboard'),
]
