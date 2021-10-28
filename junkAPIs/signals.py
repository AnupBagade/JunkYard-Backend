from django.dispatch import receiver
import django.dispatch

delete_item_image = django.dispatch.Signal(providing_args=['image_path'])

delete_menu_image = django.dispatch.Signal(providing_args=['image_path'])