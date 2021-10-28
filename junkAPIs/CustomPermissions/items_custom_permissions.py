from rest_framework.permissions import BasePermission


class ItemsCustomPermission(BasePermission):

    message = 'User has to be authenticated. User has to be staff/superuser.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return False