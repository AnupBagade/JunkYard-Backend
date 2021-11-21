# Generated by Django 3.2.8 on 2021-11-07 18:24

import django.core.validators
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('junkAPIs', '0005_alter_approvedorders_order_items'),
    ]

    operations = [
        migrations.AddField(
            model_name='approvedorders',
            name='order_delivery_address',
            field=models.TextField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='approvedorders',
            name='order_user_mobile_number',
            field=models.CharField(default=1231231231, max_length=10, validators=[django.core.validators.RegexValidator(message='Invalid phone number format', regex='^[\\d]{10}$')]),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pendingorders',
            name='order_delivery_address',
            field=models.TextField(default='test'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='pendingorders',
            name='order_user_mobile_number',
            field=models.CharField(default=1231231231, max_length=10, validators=[django.core.validators.RegexValidator(message='Invalid phone number format', regex='^[\\d]{10}$')]),
            preserve_default=False,
        ),
    ]
