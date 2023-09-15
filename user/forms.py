import re

from django import forms

from user.models import CustomUser

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python


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

        if CustomUser.objects.filter(email=email).exists():
            self.add_error("email", "Email is already taken.")

        # if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        #     self.add_error("email", "Invalid email format.")

        # #phone validation
        # phone_number = cleaned_data.get("phone_number")

        # if not phone_number:
        #     return None  # Return None if the field is empty

        # # Use the to_python method to convert the input to a PhoneNumber object
        # phone_number = to_python(phone_number)

        # if not phone_number.is_valid():
        #     raise forms.ValidationError('Invalid phone number')

        # return phone_number


