# Generated by Django 4.0.4 on 2023-09-29 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0021_rename_product_price_per_unit_order_order_total_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='product_qty',
            field=models.PositiveBigIntegerField(default=1),
            preserve_default=False,
        ),
    ]
