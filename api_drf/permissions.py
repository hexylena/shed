from rest_framework import permissions
from base.models import Version, Installable


class InstallableAttachedOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow users associated with an installable to
    edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Installable):
            return obj.is_editable_by(request.user)
        elif isinstance(obj, Version):
            return obj.installable.is_editable_by(request.user)

        return False


class VersionPostOnly(permissions.BasePermission):
    """
    Custom permission to only allow users associated with an installable to
    create new versions.

    PUT/PATCH/DELETE methods are not permitted for version objects, only POST.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.method == 'POST':
            return True

        # Updating existing releases is NOT permitted
        return False


class ReadOnly(permissions.BasePermission):
    """Some of our data is read-only and must NEVER be modified"""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS
