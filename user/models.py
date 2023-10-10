import random
import uuid

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager
from django.core.files.storage import default_storage

from PIL import Image

from phonenumber_field.modelfields import PhoneNumberField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)
    

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('amount', 'Amount'),
        ('percent', 'Percent'),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=50)
    discount_type = models.CharField(max_length=100, choices=DISCOUNT_TYPE_CHOICES)
    amount_or_percent = models.DecimalField(max_digits=5, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.code
    
    def save(self, *args, **kwargs):
        unique_number = random.randint(1000, 9999)
        self.code = self.code + str(unique_number)
        super(Coupon, self).save(*args, **kwargs)

    def is_valid(self):
        now = timezone.now()
        return self.valid_from <= now <= self.valid_to and self.active
    

class CustomUser(AbstractUser, PermissionsMixin):
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True)
    referral_code = models.CharField(max_length=20, null=True, blank=True, unique=True)
    used_code = models.CharField(max_length=20, null=True, blank=True)
    is_blocked = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        unique_id = str(uuid.uuid4().hex[:6]) 
        self.referral_code = "FASHION" + unique_id
        if self.profile_picture and hasattr(self.profile_picture, 'path'):
            try:
                with default_storage.open(self.profile_picture.path, 'rb') as img_file:
                    img = Image.open(img_file)
                    img = img.resize((150, 150), Image.LANCZOS)
                    img.save(self.profile_picture.path, img.format)
            except FileNotFoundError:
                pass

        super().save(*args, **kwargs)
    

class CouponUsage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    date_used = models.DateTimeField(auto_now_add=True)


class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    address_line1 = models.CharField(max_length=250)
    address_line2 = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    pin_code = models.PositiveBigIntegerField()
    phone_number = PhoneNumberField()
    state = models.CharField(max_length=150)
    is_default = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Address'

    def __str__(self):
        return self.first_name + " " + self.last_name


class Wallet(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def __str__(self):
        return f"Wallet of {self.user.first_name}"
    

class ReferralAmount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
       return str(self.amount)