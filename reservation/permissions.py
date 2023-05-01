from rest_framework.permissions import BasePermission
from rest_framework import permissions


class CanAddOrUpdateProperty(BasePermission):
    """
    Custom permission class for admin or host user to add or update property
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        host_user = bool(request.user and request.user.role == 'host')
        admin_user = bool(request.user and request.user.is_superuser)
        return host_user or admin_user


class AdminOnlyActions(BasePermission):
    """
    Custom permission class for admin only actions
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_superuser)


class CanAddOrUpdateReservation(BasePermission):
    """
    Custom permission class for admin or host user to make reservation
    """

    def has_permission(self, request, view):
        guest_user = bool(request.user and request.user.role == 'guest')
        admin_user = bool(request.user and request.user.is_superuser)
        return guest_user or admin_user
