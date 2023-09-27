from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from user.models import CustomUser, Address

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

