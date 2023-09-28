from django import forms

from user.models import CustomUser


class CustomUserEditForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'first_name', 'last_name', 'email', 'phone_number']