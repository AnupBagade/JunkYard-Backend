# Generated by Django 3.2.8 on 2021-11-10 17:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('junkAPIs', '0009_auto_20211110_2219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='approvedorders',
            name='order_delivery_employee',
        ),
        migrations.AddField(
            model_name='deliveryemployees',
            name='order_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='order_delivery_employee', to='junkAPIs.approvedorders'),
        ),
    ]
