from rest_framework.permissions import SAFE_METHODS, BasePermission


class AuthorOrReadOnly(BasePermission):
    """Object-level permission to only allow authors of an object to edit it.
    Assumes the model instance has an `author` attribute.
    """
    message = 'Редактировать чужой контент запрещено.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or obj.author == request.user
        )
