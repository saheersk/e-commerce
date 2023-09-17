import os
import uuid 

from django.db import models
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile

from PIL import Image
from io import BytesIO

from user.models import CustomUser


class Category(models.Model):
    name = models.CharField(max_length=100)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    title = models.CharField(max_length=150)
    featured_image = models.ImageField(upload_to='Product/featured-images')
    description = models.TextField()
    price = models.CharField(max_length=50)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    short_description = models.CharField(max_length=200)
    stock_unit = models.IntegerField()
    is_show = models.BooleanField(default=True)
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, blank=True)

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


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_image')
    image = models.ImageField(upload_to='Product/images')
    thumbnail = models.ImageField(upload_to='Product/thumbnails', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.thumbnail:  # Check if thumbnail field is empty
            with open(self.image.path, 'rb') as img_file:
                img = Image.open(img_file)
                img = img.resize((300, 533), Image.LANCZOS)

                # Create a thumbnail and save it to the thumbnail field
                thumbnail_img = img.copy()
                thumbnail_img.thumbnail((100, 120), Image.LANCZOS)

                # Save both the thumbnail and the original image with the same filename
                thumb_filename = os.path.basename(self.image.path)
                thumb_io = BytesIO()
                thumbnail_img.save(thumb_io, format='JPEG', quality=90)
                thumb_file = SimpleUploadedFile(thumb_filename, thumb_io.getvalue(), content_type='image/jpeg')
                self.thumbnail.save(thumb_filename, thumb_file, save=False)
                self.image.save(thumb_filename, thumb_file, save=False)



class Cart(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    qty = models.IntegerField()
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title


class Wishlist(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user =  models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.title
    

# class Order(models.Model):
#     product = models.ForeignKey(Product, on_delete=models.CASCADE)
#     user =  models.ForeignKey(User, on_delete=models.CASCADE)
#     qty = models.IntegerField()
#     added_date = models.DateTimeField(auto_now_add=True)


# class ProductImage(models.Model):
#     image = models.ImageField(upload_to='product_images/')
    # thumbnail = ImageSpecField(source='image',
    #                             processors=[ResizeToFill(100, 100)],
    #                             format='JPEG',
    #                             options={'quality': 90})



