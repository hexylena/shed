from rest_framework import permissions
from base.models import Revision, Installable


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
            return obj.can_edit(request.user)
        elif isinstance(obj, Revision):
            return obj.installable.can_edit(request.user)

        return False


class RevisionPostOnly(permissions.BasePermission):
    """
    Custom permission to only allow users associated with an installable to
    create new revisions.

    PUT/PATCH/DELETE methods are not permitted for revision objects, only POST.
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
