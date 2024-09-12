from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ProgressBarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.task_id = self.scope['url_route']['kwargs']['task_id']
        await self.channel_layer.group_add(self.task_id, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.task_id, self.channel_name)

    async def task_progress(self, event):
        progress = event['progress']
        await self.send(text_data=json.dumps({
            'progress': progress
        }))