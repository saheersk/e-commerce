import random

from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin, BaseUserManager

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
    profile_picture = models.FileField(upload_to="user/profile/", null=True, blank=True)
    phone_number = PhoneNumberField(unique=True)
    email = models.EmailField(unique=True)
    is_blocked = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone_number']

    def __str__(self):
        return self.email
    

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
