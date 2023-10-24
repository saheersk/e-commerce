from django.contrib import admin

from .models import BroadcastNotification, OrderNotification


class BroadcastNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'broadcast_on']

admin.site.register(BroadcastNotification, BroadcastNotificationAdmin)


class OrderNotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'order', 'total_amount']

admin.site.register(OrderNotification, OrderNotificationAdmin)