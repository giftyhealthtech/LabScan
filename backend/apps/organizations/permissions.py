from rest_framework.permissions import BasePermission

class IsPlatformAdmin(BasePermission):
    """
    Allows access only to platform administrators.
    """

    message = "Only platform administrators can perform this action."

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.is_superuser
        )