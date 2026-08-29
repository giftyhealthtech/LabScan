from django.db import transaction
from datetime import timedelta
from django.utils import timezone

from apps.accounts.services import create_user
from .models import Organization, OrganizationMembership, OrganizationInvitation
from .service_email import send_invitation_email

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

def create_invitation(
    *,
    organization,
    email,
    invited_by,
):
    expires_at = timezone.now() + timedelta(days=3)

    invitation =  OrganizationInvitation.objects.create(
        organization=organization,
        email=email,
        role=OrganizationMembership.Role.STAFF,
        expires_at=expires_at,
        invited_by=invited_by,
    )
    transaction.on_commit(
        lambda: send_invitation_email(invitation)
    )
    
    return invitation