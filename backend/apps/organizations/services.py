from django.db import transaction

from apps.accounts.services import create_user
from .models import Organization, OrganizationMembership

@transaction.atomic
def register_organization(
    *,
    organization_data,
    admin_data,
):
    organization = Organization.objects.create(
        **organization_data,
        status=Organization.Status.PENDING,
    )

    admin = create_user(**admin_data)

    OrganizationMembership.objects.create(
        user=admin,
        organization=organization,
        role=OrganizationMembership.Role.ADMIN,
        is_active=True,
    )

    return organization