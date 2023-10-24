from celery import shared_task
from channels.layers import get_channel_layer
from .models import BroadcastNotification
import json
import asyncio

@shared_task
def broadcast_notification(data):
    print(data, 'notification')
    try:
        notification = BroadcastNotification.objects.filter(id=int(data))
        if len(notification) > 0:
            notification = notification.first()
            channel_layer = get_channel_layer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(channel_layer.group_send(
                "notification_broadcast",
                {
                    'type': 'send_notification',
                    'message': json.dumps(notification.message),
                }))
            notification.sent = True
            notification.save()
            return 'Done'
        else:
            return "Not Found"

    except Exception as ex:
        raise ex
