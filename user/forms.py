import re

from django import forms

from user.models import CustomUser

class CustomUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "password", "phone_number", "used_code"]

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        elif len(password) < 8:
            self.add_error("password", "Password must be at least 8 characters.")

        email = cleaned_data.get("email")

        if email is not None and isinstance(email, str):
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                self.add_error("email", "Invalid email format.")
            elif CustomUser.objects.filter(email=email).exists():
                self.add_error("email", "Email is already taken.")
        else:
            self.add_error("email", "Invalid email format.")

        for field_name in ["first_name", "last_name"]:
            field_value = cleaned_data.get(field_name)
            if not field_value:
                self.add_error(field_name, f"{field_name.replace('_', ' ').title()} is required.")
            elif field_value.strip() == "":
                self.add_error(field_name, f"{field_name.replace('_', ' ').title()} cannot be only spaces.")

        return cleaned_data
