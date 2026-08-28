from rest_framework.permissions import BasePermission

from .models import OrganizationMembership

        
class IsPlatformAdmin(BasePermission):
    """
    Allows access only to platform administrators.
    """

    message = "Only platform administrators can perform this action."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_superuser

class IsOrganizationPermission(BasePermission):
    required_role = None

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        organization_id = view.kwargs.get("organization_id")

        if not organization_id:
            return False

        filters = {
            "user": request.user,
            "organization_id": organization_id,
            "is_active": True,
            "organization__status": "APPROVED",
        }

        if self.required_role:
            filters["role"] = self.required_role

        return OrganizationMembership.objects.filter(
            **filters
        ).exists()


class IsOrganizationMember(IsOrganizationPermission):
    message = "You are not a member of this organization."

class IsOrganizationAdmin(IsOrganizationPermission):
    message = "Only organization administrators can perform this action."
    required_role = OrganizationMembership.Role.ADMIN

class IsOrganizationStaff(IsOrganizationPermission):
    message = "Only organization staff can perform this action."
    required_role = OrganizationMembership.Role.STAFF    