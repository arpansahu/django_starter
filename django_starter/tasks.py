from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import time
from celery_progress_custom_app.backend import WebSocketProgressRecorder

# @shared_task(bind=True)
# def long_running_task(self):
#     channel_layer = get_channel_layer()
#     task_id = self.request.id
#     for i in range(101):
#         time.sleep(0.1)
#         progress = i
#         async_to_sync(channel_layer.group_send)(
#             task_id, 
#             {'type': 'task_progress', 'progress': progress}
#         )
#     return "Task completed"


@shared_task(bind=True)
def long_running_task(self):
    progress_recorder = WebSocketProgressRecorder(self)
    total = 100  # Simulate 100 steps
    for i in range(total):
        # Simulate work
        time.sleep(0.1)
        progress_recorder.set_progress(i + 1, total)
    return {"status": "Success", "message": "Task Completed"}

@shared_task
def demo_task():
    # Simulate a long-running task by sleeping
    time.sleep(5)
    return "Demo task completed!"