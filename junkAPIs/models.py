from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType


def items_upload_to(instance, image_name, *args, **kwargs):
    return '/'.join(['items_images', str(instance.item_type).lower(), instance.item_name+'.jpg'])


def menu_upload_to(instance, *args, **kwargs):
    return '/'.join(['menu_images', str(instance.menu_name).lower(), instance.menu_name+'.jpg'])


class Menu(models.Model):
    menu_id = models.AutoField(primary_key=True)
    menu_name = models.CharField(max_length=70, unique=True, blank=False)
    menu_name_key = models.CharField(max_length=70, unique=True, blank=False)
    menu_image = models.ImageField(upload_to=menu_upload_to, blank=False)

    def __str__(self):
        return self.menu_name_key

    class Meta:
        ordering = ['menu_name_key']


class Items(models.Model):
    ITEM_DIET_TYPE = (
        ('veg', 'Vegetarian'),
        ('nonveg', 'Non-Vegetarian'),
        ('vegan', 'Vegan')
    )

    ITEMS_TYPES = (
        ('burger', 'Burger'),
        ('pizza', 'Pizza'),
        ('sandwich', 'Sandwich'),
        ('chicken', 'Chicken'),
        ('fries', 'Fries'),
        ('dessert', 'Dessert'),
        ('donught', 'Donught'),
        ('pasta', 'Pasta'),
        ('seafood', 'Sea Food')
    )

    item_id = models.AutoField(primary_key=True)
    item_type = models.CharField(max_length=20, choices=ITEMS_TYPES)
    item_name = models.CharField(max_length=70, unique=True)
    item_name_key = models.CharField(max_length=70, unique=True)
    item_description = models.TextField()
    item_ingredients = models.TextField()
    item_image = models.ImageField(upload_to=items_upload_to, blank=False)
    item_diet_type = models.CharField(max_length=8, choices=ITEM_DIET_TYPE)
    item_calories = models.FloatField()
    item_price = models.FloatField(blank=False)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='items')

    def __str__(self):
        return self.item_name_key

    class Meta:
        ordering = ['item_name']


class JunkUserManager(BaseUserManager):

    # Method to save user to database
    def save_user(self, email, mobile_number, password, **other_fields):
        if not email:
            raise ValueError(_('Please provide valid email address.'))
        user = self.model(email=self.normalize_email(email), junkuser_mobile_number=mobile_number, **other_fields)
        user.set_password(password)
        user.save()
        if other_fields['junkuser_is_customer']:
            group_obj = Group.objects.get(name='customer_group')
            user_temp = Junkuser.objects.get(email=self.normalize_email(email), junkuser_mobile_number=mobile_number)
            user_temp.groups.add(group_obj)
            user_temp.save()
        elif other_fields['junkuser_is_employee']:
            group_obj = Group.objects.get(name='employee_group')
            user_temp = Junkuser.objects.get(email=self.normalize_email(email),
                                             junkuser_mobile_number=mobile_number)
            user_temp.groups.add(group_obj)
            user_temp.save()
        return user

    # Method to create user
    def create_user(self, email, mobile_number, password, **other_fields):
        other_fields['is_staff'] = False
        other_fields['is_superuser'] = False
        other_fields['is_active'] = True
        return self.save_user(email, mobile_number, password, **other_fields)

    # Method to create staff user
    def create_staffuser(self, email, mobile_number, password, **other_fields):
        other_fields['is_staff'] = True
        other_fields['is_superuser'] = False
        other_fields['is_active'] = True
        return self.save_user(email, mobile_number, password, **other_fields)

    # Method to create superuser
    def create_superuser(self, email, mobile_number, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)

        if other_fields.get('is_staff') is not True:
            raise ValueError('is_staff for superuser must be True')
        if other_fields.get('is_superuser') is not True:
            raise ValueError('is_superuser for superuser must be True')
        return self.save_user(email, mobile_number, password, **other_fields)


class Junkuser(AbstractBaseUser, PermissionsMixin):

    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
        ('not_specified', 'Not to specify')
    )

    MOBILE_NUMBER_VALIDATOR = RegexValidator(regex=r'^[\d]{10}$',
                                             message='Invalid phone number format')

    junkuser_id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=50, blank=False, unique=True)
    junkuser_first_name = models.CharField(max_length=30, blank=False)
    junkuser_last_name = models.CharField(max_length=30, blank=False)
    junkuser_gender = models.CharField(choices=GENDER, blank=True, max_length=15)
    junkuser_age = models.IntegerField(blank=True, null=True)
    junkuser_mobile_number = models.CharField(validators=[MOBILE_NUMBER_VALIDATOR], unique=True, max_length=10, blank=False)
    junkuser_address = models.TextField(blank=True)
    junkuser_joined = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    junkuser_is_customer = models.BooleanField(default=True, blank=False)
    junkuser_is_employee = models.BooleanField(default=False, blank=False)

    # Email is used as an identifier
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['junkuser_mobile_number', 'junkuser_age']

    # JunkUser Manager
    objects = JunkUserManager()

    class Meta:
        ordering = ['junkuser_id']

    def __str__(self):
        return (f'{self.junkuser_first_name}, {self.junkuser_last_name},' \
               f' Customer - {self.junkuser_is_customer}, Employee - {self.junkuser_is_employee}')


class PendingOrders(models.Model):

    ORDER_STATUS = 'pending'

    order_id = models.AutoField(primary_key=True, )
    order_items = models.TextField(blank=False)
    ordered_date = models.DateField(auto_now_add=True)
    ordered_timestamp = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=15, default=ORDER_STATUS)
    last_updated = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(Junkuser, on_delete=models.CASCADE, related_name='pending_orders')

    class Meta:
        ordering = ['ordered_timestamp']


class ApprovedOrders(models.Model):

    ORDER_STATUS = (
        ('in_progress', 'In-Progress'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )

    order_id = models.AutoField(primary_key=True)
    order_items = models.TextField(blank=False)
    ordered_date = models.DateField(blank=False)
    ordered_timestamp = models.DateTimeField(blank=False)
    approved_timestamp = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS, blank=False)
    order_approved_employee = models.ForeignKey(Junkuser, on_delete=models.CASCADE, related_name='orders_approved',
                                                blank=True, null=True)
    order_delivery_employee = models.ForeignKey(Junkuser, on_delete=models.CASCADE, related_name='orders_delivered',
                                                blank=True, null=True)
    user = models.ForeignKey(Junkuser, on_delete=models.CASCADE, related_name='approved_orders')
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['approved_timestamp']


class CartOrders(models.Model):

    cart_id = models.AutoField(primary_key=True)
    cart_items = models.JSONField(null=False)
    cart_user = models.ForeignKey(Junkuser, on_delete=models.CASCADE, related_name="user_cart_items")
    cart_added = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['cart_id']

