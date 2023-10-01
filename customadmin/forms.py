import re

from django import forms

from user.models import CustomUser
from web.models import Banner
from shop.models import Category, Product, ProductImage, Order, ProductVariant

from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.phonenumber import to_python


class AdminCustomUserForm(forms.ModelForm):
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email" , "phone_number", "password", "confirm_password", "is_superuser", "is_blocked"]

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        email = cleaned_data.get("email")
        confirm_password = cleaned_data.get("confirm_password")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if not first_name:
            self.add_error("first_name", "First name is required")
        
        if not last_name:
            self.add_error("last_name", "Last name is required")

        if not email:
            self.add_error("last_name", "Last name is required")

        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")

        if CustomUser.objects.filter(email=email).exists():
            self.add_error("email", "Email is already taken.")

        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            self.add_error("email", "Invalid email format.")



class AdminCustomUpdateUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["first_name", "last_name", "email", "phone_number","is_superuser", "is_blocked"]

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")

        if not first_name:
            self.add_error("first_name", "First name is required")
        
        if not last_name:
            self.add_error("last_name", "Last name is required")

        if not email:
            self.add_error("last_name", "Last name is required")

        if not email:
            self.add_error("email", "Email is required.")
            return

        if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
            self.add_error("email", "Invalid email format.")


class AdminCustomBlockUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["is_blocked"]


class AdminCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'is_blocked']

    def clean_name(self):
        name = self.cleaned_data.get('name')
        instance = self.instance

        if Category.objects.filter(name=name).exclude(pk=instance.pk).exists():
            if Category.objects.filter(name=name).exclude(pk=instance.pk).exists() and Category.objects.filter(name=name, is_deleted = True):
                cat = Category.objects.get(name=name)
                cat.is_deleted = False
                cat.save()
            else:
                self.add_error('name', "A category with this name already exists.")

        return name



class AdminProduct(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['title', 'featured_image', 'description', 'short_description', 'category', 'price']


class AdminProductImage(forms.ModelForm):
    image = forms.ImageField(required=False)
    class Meta:
        model = ProductImage
        fields = ['image']


class AdminOrderFrom(forms.ModelForm):

    class Meta:
        model = Order
        fields = ['order_status']


class AdminProductVariantFrom(forms.ModelForm):

    class Meta:
        model = ProductVariant
        exclude = ['variant_name']



class AdminBannerForm(forms.ModelForm):

    class Meta:
        model = Banner
        fields = '__all__'