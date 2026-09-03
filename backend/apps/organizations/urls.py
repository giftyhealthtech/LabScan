from django.urls import path

from .views import (
    OrganizationRegistrationView,
    PendingOrganizationsView,
    ApproveOrganizationView,
    InvitationView,
    AcceptInvitationView,
)

urlpatterns = [
    path(
        "register/",
        OrganizationRegistrationView.as_view(),
        name="organization-register",
    ),
    path(
       "platform/pending/",
        PendingOrganizationsView.as_view(),
        name="pending-organizations",
    ),
    path(
       "platform/<int:pk>/approve/",
        ApproveOrganizationView.as_view(),
        name="approve-organizations",
    ),
    path(
        "<int:organization_id>/invitations/",
        InvitationView.as_view(),
        name="organization-invite-staff",
    ),
    path(
        "invitations/<uuid:invitation_token>/accept/",
        AcceptInvitationView.as_view(),
        name="organization-accept-invitation",
    )
]