from fashion_asgi.models import BroadcastNotification


def notification(request):
    if request.user.is_authenticated:
        return {'notification': BroadcastNotification.objects.filter(sent=True) }