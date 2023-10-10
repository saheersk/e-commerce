from django import forms

from user.models import CustomUser, Address
from shop.models import OrderManagement, UserReview


class CustomUserEditForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = ['profile_picture', 'first_name', 'last_name', 'email', 'phone_number']


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'phone_number', 'state', 'country', 'city', 'address_line1', 'address_line2', 'pin_code']

    def clean(self):
        cleaned_data = super().clean()

        required_fields = ['first_name', 'last_name', 'phone_number', 'state', 'country', 'city', 'address_line1', 'address_line2', 'pin_code']
        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, "This field is required.")
                break

        return cleaned_data
    

class PasswordResetRequestForm(forms.Form):
    email = forms.EmailField()


class OrderManagementForm(forms.ModelForm):
    class Meta:
        model = OrderManagement
        fields = ['reason', 'message']


class UserReviewForm(forms.ModelForm):
    
    class Meta:
        model = UserReview
        fields = ['comment', 'rating']