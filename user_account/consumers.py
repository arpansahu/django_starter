"""
WebSocket consumer for real-time user notifications.

Sends toast notifications to connected users via their personal channel group.
Each authenticated user joins group 'notifications_{user_id}'.
"""
import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    """
    Per-user notification WebSocket.
    
    Connect: ws://<host>/ws/notifications/
    Requires authenticated user (via AuthMiddlewareStack).
    
    Receives messages of type 'send_notification' from channel layer:
    {
        "type": "send_notification",
        "notification": {
            "title": "...",
            "message": "...",
            "level": "success" | "info" | "warning" | "error",
            "icon": "fa-icon-class" (optional),
            "timestamp": "ISO 8601" (optional, auto-added if missing),
        }
    }
    """

    async def connect(self):
        self.user = self.scope.get('user')
        if self.user and self.user.is_authenticated:
            self.group_name = f'notifications_{self.user.id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            logger.debug("Notification WS connected for user %s", self.user.id)
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            logger.debug("Notification WS disconnected for user %s", self.user.id)

    async def receive(self, text_data):
        # Client doesn't send messages; this is server → client only
        pass

    async def send_notification(self, event):
        """Handle 'send_notification' messages from the channel layer."""
        notification = event.get('notification', {})
        await self.send(text_data=json.dumps(notification))
