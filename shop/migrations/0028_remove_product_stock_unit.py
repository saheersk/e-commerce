# Generated by Django 4.0.4 on 2023-10-01 06:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0027_alter_productvariant_color'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='stock_unit',
        ),
    ]