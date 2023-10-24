from fashion_asgi.models import BroadcastNotification, OrderNotification


def notification(request):
    if request.user.is_authenticated:
        return {'notification': BroadcastNotification.objects.filter(sent=True) }
    else:
        return {'notification': ''}


def order_notification(request):
    if request.user.is_authenticated:
        return {'order_notification': OrderNotification.objects.all()}
    else:
        return {'order_notification': ''}