from django.urls import path

from .views import OrganizationRegistrationView

urlpatterns = [
    path(
        "register/",
        OrganizationRegistrationView.as_view(),
        name="organization-register",
    ),
]
