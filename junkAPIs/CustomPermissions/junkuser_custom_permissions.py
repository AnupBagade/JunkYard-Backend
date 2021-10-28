from rest_framework import permissions
from junkAPIs.models import Junkuser


class JunkuserCustomPermission(permissions.BasePermission):

    message = "User has to be authenticated and Only Staff has access."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.user.junkuser_is_employee and not obj.junkuser_is_customer:
            return True
        return False


class JunkuserDetailCustomPermission(permissions.BasePermission):

    message = "User has to be authenticated. User has to be superuser or should be author to edit."

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        # if request.method not in permissions.SAFE_METHODS:
        #     return False
        if request.user.junkuser_is_employee and request.user.email == obj.email:
            return True
        if request.user.email == obj.email and request.user.junkuser_is_customer:
            return True
        return False


