from rest_framework.permissions import BasePermission


class CartOrderCustomPermission(BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.email == obj.cart_user.email:
            return True
        return False