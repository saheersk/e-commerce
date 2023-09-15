from django.db import models


class Banner(models.Model):
    title = models.CharField(max_length=150)
    short_description = models.CharField(max_length=250)
    image = models.FileField(upload_to="banner/images/")
    category = models.CharField(max_length=100)
    added_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Newsletter(models.Model):
    email = models.EmailField(unique=True)
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email
    

class Contact(models.Model):
    full_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    message = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name
    

class FashionTrends(models.Model):
    image = models.FileField(upload_to="fashion/images/")
    title = models.CharField(max_length=50)
    added_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Fashion Trends"
        
    def __str__(self):
        return self.title
    

class Showcase(models.Model):
    image = models.FileField(upload_to="showcase/images/")
    title = models.CharField(max_length=50)
    added_date = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title

