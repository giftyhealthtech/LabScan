from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User

def create_user(email, password, **extra_fields):
   
    user = User.objects.create_user(email=email, password=password, **extra_fields)
    return user

def create_tokens(user):
    refresh = RefreshToken.for_user(user)

    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }

def login_user(*, email, password, request=None):
    email = email.lower().strip()

    user = authenticate(
        request=request,
        username=email,
        password=password,
    )

    if user is None:
        raise serializers.ValidationError(
            "Invalid email or password."
        )

    if not user.is_active:
        raise serializers.ValidationError(
            "This account is inactive."
        )

    if user.is_superuser:
        return {
            "user": user,
            "membership": None,
        }

    membership = (
        user.organization_memberships
        .select_related("organization")
        .filter(is_active=True)
        .first()
    )

    if membership is None:
        raise serializers.ValidationError(
            "You are not associated with an organization."
        )

    organization = membership.organization

    if organization.status == organization.Status.PENDING:
        raise serializers.ValidationError(
            "Your organization is still awaiting approval."
        )

    if organization.status == organization.Status.REJECTED:
        raise serializers.ValidationError(
            "Your organization registration was rejected."
        )

    if organization.status == organization.Status.SUSPENDED:
        raise serializers.ValidationError(
            "Your organization has been suspended."
        )

    if organization.status != organization.Status.APPROVED:
        raise serializers.ValidationError(
            "Your organization is not approved."
        )

    return {
        "user": user,
        "membership": membership,
    }