from django.contrib import admin
from .models import BroadcastNotification


class BroadcastNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'broadcast_on']

admin.site.register(BroadcastNotification, BroadcastNotificationAdmin)