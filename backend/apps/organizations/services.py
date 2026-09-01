from django.db import transaction
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

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

# @transaction.atomic
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

def validate_invitation(invitation):
    if invitation.status != OrganizationInvitation.Status.PENDING:
        raise ValueError(
            "This invitation is no longer valid."
        )

    if invitation.expires_at <= timezone.now():
        invitation.status = OrganizationInvitation.Status.EXPIRED
        invitation.save(update_fields=["status"])

        raise ValueError(
            "This invitation has expired."
        )

    if invitation.organization.status != "APPROVED":
        raise ValueError(
            "This organization is not currently approved."
        )
        
@transaction.atomic
def accept_invitation(
    *,
    invitation_token,
    authenticated_user=None,
    first_name=None,
    last_name=None,
    phone=None,
    password=None,
):
    User = get_user_model()
    try:
        invitation = (
            OrganizationInvitation.objects
            .select_related("organization")
            .select_for_update()
            .get(token=invitation_token)
        )

    except OrganizationInvitation.DoesNotExist:
        raise ValueError("Invitation not found.")

    validate_invitation(invitation)
    existing_user = User.objects.filter(email__iexact=invitation.email).first()

    if existing_user:
        if authenticated_user is None:
            raise ValueError(
                "Login to accept this invitation."
            )

        if authenticated_user.pk != existing_user.pk:
            raise ValueError(
                "This invitation is not for you."
            )

        user = existing_user
    else:

        if not password:
            raise ValueError(
                "Password is required."
            )

        if not first_name:
            raise ValueError(
                "First name is required."
            )

        if not last_name:
            raise ValueError(
                "Last name is required."
            )

        user = create_user(
            email=invitation.email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        ) 
    
    membership, created = OrganizationMembership.objects.get_or_create(
        user=user,
        organization=invitation.organization,
        defaults={
            "role": invitation.role,
            "is_active": True,
        },
    )

    if not created:
        membership.role = invitation.role
        membership.is_active = True
        membership.save(
            update_fields=[
                "role",
                "is_active",
            ]
        )

    invitation.status = OrganizationInvitation.Status.ACCEPTED
    invitation.accepted_at = timezone.now()

    invitation.save(
        update_fields=[
            "status",
            "accepted_at",
        ]
    )

    return user, membership