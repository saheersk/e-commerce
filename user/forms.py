import re

from django import forms

from user.models import CustomUser


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




    


