from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
        or request.user.is_authenticated
        )

    def has_object_permissions(self, request, view, object):
        if request.method in permissions.SAFE_METHODS:
            return True
        return object.author == request.user
