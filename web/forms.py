import re

from django import forms

from web.models import Contact


class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = ['full_name', 'email', 'message']

    def clean(self):
        cleaned_data = super().clean()

        email = cleaned_data.get("email")
        full_name = cleaned_data.get("full_name")
        message = cleaned_data.get("message")

        if email:
            if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
                self.add_error("email", "Invalid email format.")

        if not full_name:
            self.add_error("full_name", "Full name is required.")

        if not message:
            self.add_error("message", "Message is required.")