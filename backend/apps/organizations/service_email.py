from django.conf import settings
from django.core.mail import send_mail

from .models import OrganizationInvitation

def send_invitation_email(invitation):
    invitation_url = (
        f"{settings.FRONTEND_URL}"
        f"/invitations/{invitation.token}"
    )

    subject = (
        f"Invitation to join "
        f"{invitation.organization.name}"
    )

    message = f"""
Hello,

You have been invited to join {invitation.organization.name}
as a staff member.

Please click the link below to accept your invitation:

{invitation_url}

This invitation expires on:
{invitation.expires_at.strftime("%B %d, %Y at %H:%M UTC")}

If you did not expect this invitation, you can safely ignore
this email.

Regards,
{invitation.organization.name}
""".strip()

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invitation.email],
    )