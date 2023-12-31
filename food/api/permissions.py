from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):

    def has_object_permissions(self, request, view, object):
        return (request.method in permissions.SAFE_METHODS
                or object.author == request.user)
