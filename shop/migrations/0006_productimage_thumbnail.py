# Generated by Django 4.2.5 on 2023-09-16 07:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0005_product_featured_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='productimage',
            name='thumbnail',
            field=models.ImageField(blank=True, null=True, upload_to='Product/thumbnails'),
        ),
    ]
