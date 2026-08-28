from django.urls import path

from .views import (
    OrganizationRegistrationView,
    PendingOrganizationsView,
    ApproveOrganizationView,
    InvitationView,
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
)
]