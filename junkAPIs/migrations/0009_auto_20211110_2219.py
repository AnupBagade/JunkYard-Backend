# Generated by Django 3.2.8 on 2021-11-10 16:49

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('junkAPIs', '0008_deliveryemployees'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='deliveryemployees',
            options={'ordering': ['delivery_employee_id']},
        ),
        migrations.RemoveField(
            model_name='deliveryemployees',
            name='order_id',
        ),
        migrations.AlterField(
            model_name='approvedorders',
            name='order_delivery_employee',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_deliverey', to=settings.AUTH_USER_MODEL),
        ),
    ]
