import json

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django_celery_beat.models import MINUTES, PeriodicTask, CrontabSchedule, PeriodicTasks
from django.core import serializers

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import asyncio

from shop.models import Order


class BroadcastNotification(models.Model):
    message = models.CharField(max_length=200)
    broadcast_on = models.DateTimeField()
    sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-broadcast_on']

@receiver(post_save, sender=BroadcastNotification)
def notification_handler(sender, instance, created, **kwargs):
    print('notification handler')
    if created:
        print(created, 'create')
        schedule, created = CrontabSchedule.objects.get_or_create(hour = instance.broadcast_on.hour, minute = instance.broadcast_on.minute, day_of_month = instance.broadcast_on.day, month_of_year = instance.broadcast_on.month)
        task = PeriodicTask.objects.create(crontab=schedule, name="broadcast-notification-"+str(instance.id), task="fashion_asgi.tasks.broadcast_notification", args=json.dumps((instance.id,)))


class OrderNotification(models.Model):
    full_name = models.CharField(max_length=100)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    total_amount = models.CharField(max_length=100)
    added_date = models.DateTimeField(auto_now_add=True)

@receiver(post_save, sender=OrderNotification)
def send_notification_to_admin(sender, instance, created, **kwargs):
    if created:
        try:
            order_data = {
                "order_items": [
                    {
                        "id": item.id,  # Include the order_items.id
                        "product_title": item.product.title
                    }
                    for item in instance.order.order_items.all()
                ],
            }

            message = {
                "full_name": instance.full_name,
                "order_data": order_data,
                "total_amount": str(instance.total_amount),
            }

            channel_layer = get_channel_layer()
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(channel_layer.group_send(
                "notification_admin",
                {
                    'type': 'send_notification_admin',  # Update the message type here
                    'message': json.dumps(message),
                }))
        except Exception as ex:
            raise ex