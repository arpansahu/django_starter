from django.urls import re_path
from .consumers import ProgressBarConsumer 

websocket_urlpatterns = [
    re_path(r'ws/progress/(?P<task_id>[0-9a-f-]+)/$', ProgressBarConsumer.as_asgi()),
]