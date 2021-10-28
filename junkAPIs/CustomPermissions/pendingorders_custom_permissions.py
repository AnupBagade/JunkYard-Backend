from rest_framework.permissions import BasePermission


class PendingOrdersCustomPermission(BasePermission):

    message = 'User has to be authenticated. User has to be staff or owner of the order.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.junkuser_is_employee and request.user.is_superuser:
            return True
        if request.user.junkuser_is_customer and request.user.email == obj.email:
            return True
        return False
