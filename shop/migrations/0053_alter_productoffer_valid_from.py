# Generated by Django 4.0.4 on 2023-10-09 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0052_rename_discountcategoryoffer_categoryoffer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productoffer',
            name='valid_from',
            field=models.DateTimeField(),
        ),
    ]
