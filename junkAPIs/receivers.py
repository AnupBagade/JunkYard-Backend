from django.dispatch import receiver
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from .signals import *
from django.db.models.signals import post_delete, pre_save, post_save
from .models import Items, Menu
import os


@receiver(delete_item_image)
def delete_unused_item_image(sender, image_path, **kwargs):
    if image_path:
        try:
            os.remove(image_path)
        except FileNotFoundError:
            raise FileNotFoundError


@receiver(post_delete, sender=Items)
def delete_item_image(sender, instance, **kwargs):
    try:
        if os.path.isfile(instance.item_image.path):
            os.remove(instance.item_image.path)
    except FileNotFoundError:
        raise FileNotFoundError


@receiver(delete_menu_image)
def delete_unused_menu_image(sender, image_path, **kwargs):
    if image_path:
        try:
            os.remove(image_path)
        except FileNotFoundError:
            raise FileNotFoundError


@receiver(post_delete, sender=Menu)
def delete_menu_image(sender, instance, **kwargs):
    try:
        if os.path.isfile(instance.menu_image.path):
            os.remove(instance.menu_image.path)
    except FileNotFoundError:
        raise FileNotFoundError