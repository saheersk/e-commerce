from django.contrib import admin

from web.models import Banner, Contact, Newsletter, FashionTrends, Showcase


class BannerAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category']

admin.site.register(Banner, BannerAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email']

admin.site.register(Contact, ContactAdmin)


class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['id', 'email']

admin.site.register(Newsletter, NewsletterAdmin)


class ShowcaseAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

admin.site.register(Showcase, ShowcaseAdmin)


class FashionAdmin(admin.ModelAdmin):
    list_display = ['id', 'title']

admin.site.register(FashionTrends, FashionAdmin)