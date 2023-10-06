from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import CustomUser, Address, Coupon, CouponUsage, Wallet

class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone_number')

    fieldsets = (
        *UserAdmin.fieldsets,
        (
            'User Extra Details',
            {
                'fields': (
                    'phone_number',
                    'profile_picture', 
                    'is_blocked'
                ),
            }
        ),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email','phone_number', 'password1', 'password2'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)


class AddressAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'pin_code']

admin.site.register(Address, AddressAdmin)


class CouponAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'discount_type', 'amount_or_percent']

admin.site.register(Coupon, CouponAdmin)


class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'coupon']

admin.site.register(CouponUsage, CouponUsageAdmin)


class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance']

admin.site.register(Wallet, WalletAdmin)