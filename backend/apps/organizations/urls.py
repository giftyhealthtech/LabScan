from django.urls import path

from .views import (
    OrganizationRegistrationView,
    PendingOrganizationsView,
    ApproveOrganizationView,
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
]
