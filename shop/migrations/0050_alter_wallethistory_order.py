# Generated by Django 4.0.4 on 2023-10-09 08:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0049_wallethistory_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wallethistory',
            name='order',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='shop.order'),
        ),
    ]