# Generated by Django 3.2.8 on 2021-10-28 18:17

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import junkAPIs.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Junkuser',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('junkuser_id', models.AutoField(primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=50, unique=True)),
                ('junkuser_first_name', models.CharField(max_length=30)),
                ('junkuser_last_name', models.CharField(max_length=30)),
                ('junkuser_gender', models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other'), ('not_specified', 'Not to specify')], max_length=15)),
                ('junkuser_age', models.IntegerField(blank=True, null=True)),
                ('junkuser_mobile_number', models.CharField(max_length=10, unique=True, validators=[django.core.validators.RegexValidator(message='Invalid phone number format', regex='^[\\d]{10}$')])),
                ('junkuser_address', models.TextField(blank=True)),
                ('junkuser_joined', models.DateTimeField(auto_now_add=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_superuser', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('junkuser_is_customer', models.BooleanField(default=True)),
                ('junkuser_is_employee', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['junkuser_id'],
            },
        ),
        migrations.CreateModel(
            name='Menu',
            fields=[
                ('menu_id', models.AutoField(primary_key=True, serialize=False)),
                ('menu_name', models.CharField(max_length=70, unique=True)),
                ('menu_name_key', models.CharField(max_length=70, unique=True)),
                ('menu_image', models.ImageField(upload_to=junkAPIs.models.menu_upload_to)),
            ],
            options={
                'ordering': ['menu_name_key'],
            },
        ),
        migrations.CreateModel(
            name='PendingOrders',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_items', models.TextField()),
                ('ordered_date', models.DateField(auto_now_add=True)),
                ('ordered_timestamp', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(default='pending', max_length=15)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pending_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['ordered_timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Items',
            fields=[
                ('item_id', models.AutoField(primary_key=True, serialize=False)),
                ('item_type', models.CharField(choices=[('burger', 'Burger'), ('pizza', 'Pizza'), ('sandwich', 'Sandwich'), ('chicken', 'Chicken'), ('fries', 'Fries'), ('dessert', 'Dessert'), ('donught', 'Donught'), ('pasta', 'Pasta'), ('seafood', 'Sea Food')], max_length=20)),
                ('item_name', models.CharField(max_length=70, unique=True)),
                ('item_name_key', models.CharField(max_length=70, unique=True)),
                ('item_description', models.TextField()),
                ('item_ingredients', models.TextField()),
                ('item_image', models.ImageField(upload_to=junkAPIs.models.items_upload_to)),
                ('item_diet_type', models.CharField(choices=[('veg', 'Vegetarian'), ('nonveg', 'Non-Vegetarian'), ('vegan', 'Vegan')], max_length=8)),
                ('item_calories', models.FloatField()),
                ('item_price', models.FloatField()),
                ('menu', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='junkAPIs.menu')),
            ],
            options={
                'ordering': ['item_name'],
            },
        ),
        migrations.CreateModel(
            name='CartOrders',
            fields=[
                ('cart_id', models.AutoField(primary_key=True, serialize=False)),
                ('cart_items', models.JSONField()),
                ('cart_added', models.DateTimeField(auto_now=True)),
                ('cart_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_cart_items', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['cart_id'],
            },
        ),
        migrations.CreateModel(
            name='ApprovedOrders',
            fields=[
                ('order_id', models.AutoField(primary_key=True, serialize=False)),
                ('order_items', models.TextField()),
                ('ordered_date', models.DateField()),
                ('ordered_timestamp', models.DateTimeField()),
                ('approved_timestamp', models.DateTimeField(auto_now_add=True)),
                ('order_status', models.CharField(choices=[('in_progress', 'In-Progress'), ('dispatched', 'Dispatched'), ('delivered', 'Delivered'), ('completed', 'Completed'), ('cancelled', 'Cancelled')], max_length=20)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('order_approved_employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_approved', to=settings.AUTH_USER_MODEL)),
                ('order_delivery_employee', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders_delivered', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approved_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['approved_timestamp'],
            },
        ),
    ]