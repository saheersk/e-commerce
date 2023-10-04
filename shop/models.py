import os
import uuid 

from django.db import models
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from io import BytesIO

from user.models import CustomUser, Address, Coupon


class Category(models.Model):
    name = models.CharField(max_length=100)
    is_blocked = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'categories'
    

class Product(models.Model):
    title = models.CharField(max_length=150)
    featured_image = models.ImageField(upload_to='Product/featured-images')
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=200)
    is_show = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_date']    
 
    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        slug = slugify(self.title)
        
        unique_id = str(uuid.uuid4().hex[:6]) 
        slug = f"{slug}-{unique_id}"
            
        self.slug = slug
        super().save(*args, **kwargs)

        with open(self.featured_image.path, 'rb') as img_file:
            img = Image.open(img_file)
            img = img.resize((262, 260), Image.Resampling.LANCZOS)
            img.save(self.featured_image.path, img.format)


class ProductVariant(models.Model):
    SIZE_CHOICES = (
        ('S', 'Small'),
        ('M', 'Medium'),
        ('L', 'Large'),
        ('XL', 'Extra Large'),
    )

    variant_name = models.CharField(max_length=200, unique=True)
    stock_unit = models.PositiveBigIntegerField()
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.CharField(max_length=2, choices=SIZE_CHOICES)
    is_featured = models.BooleanField(default=True)

    def __str__(self):
        return self.variant_name
    
    class Meta:
        unique_together = ('product', 'size')

    def save(self, *args, **kwargs):
        self.variant_name = self.product.title + ' ' + self.size
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    image = models.ImageField(upload_to='Product/images', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='Product/thumbnails', blank=True, null=True)
    is_show = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.thumbnail:
            if self.image:  
                with open(self.image.path, 'rb') as img_file:
                    img = Image.open(img_file)
                    img = img.resize((300, 533), Image.LANCZOS)

                    thumbnail_img = img.copy()
                    thumbnail_img.thumbnail((100, 120), Image.LANCZOS)

                    thumb_filename = os.path.basename(self.image.path)
                    thumb_io = BytesIO()
                    thumbnail_img.save(thumb_io, format='JPEG', quality=90)
                    thumb_file = SimpleUploadedFile(thumb_filename, thumb_io.getvalue(), content_type='image/jpeg')
                    self.thumbnail.save(thumb_filename, thumb_file, save=False)
                    self.image.save(thumb_filename, thumb_file, save=False)


class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    qty = models.PositiveIntegerField(default=1)
    total_price_of_product = models.DecimalField(max_digits=10, decimal_places=2)
    size = models.CharField(max_length=100)
    added_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.product.title


class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.product.title
    

class OrderStatus(models.Model):
    status = models.CharField(max_length=150)

    class Meta:
        verbose_name_plural = 'Order Status'

    def __str__(self):
        return self.status


class OrderItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    size = models.CharField(max_length=100)
    order_status = models.ForeignKey(OrderStatus, on_delete=models.CASCADE)
    total_product_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.product.title
    

class Order(models.Model):
    order_items = models.ManyToManyField(OrderItem)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(Address, on_delete=models.CASCADE)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    purchased_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)
    

class PaymentMethod(models.Model):
    payment_type = models.CharField(max_length=100)

    def __str__(self):
        return self.payment_type


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    transaction_id = models.CharField(max_length=150)
    purchased_price =models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return self.user.first_name