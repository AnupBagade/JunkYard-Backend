from rest_framework.permissions import BasePermission


class MenuCustomPermission(BasePermission):

    message = 'User has to be authenticated to view and should be superuser to modify.'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return False
