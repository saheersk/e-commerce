import re

from django import forms

from user.models import CustomUser, Address


class CustomUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email" , "password", "phone_number", "confirm_password"]

    def clean(self):
        cleaned_data = super().clean()

        #password validation
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        #email validation
        email = cleaned_data.get("email")

        if email:
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                self.add_error("email", "Invalid email format.")
            
            if CustomUser.objects.filter(email=email).exists():
                self.add_error("email", "Email is already taken.")


class AddressForm(forms.ModelForm):

    class Meta:
        model = Address
        fields = ['first_name', 'last_name', 'phone_number', 'state', 'city', 'address_line1', 'address_line2', 'pin_code']

    def clean(self):
        cleaned_data = super().clean()

        required_fields = ['first_name', 'last_name', 'phone_number', 'state', 'city', 'address_line1', 'address_line2', 'pin_code']
        for field_name in required_fields:
            if not cleaned_data.get(field_name):
                self.add_error(field_name, "This field is required.")
                break

        return cleaned_data

    


