from django.urls import re_path

from .consumers import NotificationConsumer, NotificationConsumerAdmin

websocket_urlpatterns = [
    re_path(r"ws/notification/(?P<room_name>\w+)/$", NotificationConsumer.as_asgi()),
    re_path(r"ws/notification/admin/(?P<room_name>\w+)/$", NotificationConsumerAdmin.as_asgi()),
]