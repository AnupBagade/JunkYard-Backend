# Generated by Django 3.2.8 on 2021-11-10 15:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('junkAPIs', '0007_auto_20211110_2031'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeliveryEmployees',
            fields=[
                ('delivery_employee_id', models.AutoField(primary_key=True, serialize=False)),
                ('employee_availability', models.BooleanField(default=True)),
                ('junkuser', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='is_delivery', to=settings.AUTH_USER_MODEL)),
                ('order_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='delivery_employee', to='junkAPIs.approvedorders')),
            ],
            options={
                'ordering': ['order_id'],
            },
        ),
    ]