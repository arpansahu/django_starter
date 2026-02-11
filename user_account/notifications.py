"""
Utility to push real-time notifications to users via WebSocket channel layer.

Usage:
    from user_account.notifications import notify_user
    notify_user(user_id, "Account Connected", "Your Google account is now linked.", level="success")
"""
import logging
from datetime import datetime, timezone

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def notify_user(user_id, title, message, level="info", icon=None):
    """
    Send a real-time notification to a specific user via WebSocket.
    
    Args:
        user_id: The user's primary key.
        title: Notification title (short).
        message: Notification body text.
        level: One of 'success', 'info', 'warning', 'error'.
        icon: Optional Font Awesome icon class (e.g. 'fa-google').
    """
    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("Channel layer not available; notification not sent.")
        return

    notification = {
        "title": title,
        "message": message,
        "level": level,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if icon:
        notification["icon"] = icon

    group_name = f"notifications_{user_id}"
    try:
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "send_notification",
                "notification": notification,
            },
        )
        logger.debug("Notification sent to user %s: %s", user_id, title)
    except Exception as e:
        logger.warning("Failed to send notification to user %s: %s", user_id, e)
