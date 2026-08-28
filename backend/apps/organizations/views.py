from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .services import create_invitation
from .models import Organization, OrganizationMembership
from .permissions import (
    IsPlatformAdmin,
    IsOrganizationAdmin,
)
from .serializers import (
    OrganizationRegistrationSerializer,
    OrganizationApprovalSerializer,
    OrganizationInvitationSerializer,
)


class OrganizationRegistrationView(APIView):

    def post(self, request):
        serializer = OrganizationRegistrationSerializer(
            data=request.data
        )

        serializer.is_valid(raise_exception=True)

        organization = serializer.save()

        return Response(
            {
                "message": (
                    "Organization registration submitted "
                    "successfully and is awaiting approval."
                ),
                "organization": {
                    "id": organization.id,
                    "name": organization.name,
                    "status": organization.status,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class PendingOrganizationsView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    def get(self, request):
        organizations = Organization.objects.filter(
            status=Organization.Status.PENDING
        ).order_by("-created_at")

        serializer = OrganizationApprovalSerializer(
            organizations,
            many=True
        )

        return Response(serializer.data)
    
    
class ApproveOrganizationView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsPlatformAdmin,
    ]

    def post(self, request, pk):
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "Organization not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if organization.status != Organization.Status.PENDING:
            return Response(
                {
                    "detail": (
                        "Only pending organizations "
                        "can be approved."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        organization.status = Organization.Status.APPROVED
        organization.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
        return Response(
            {
                "message": "Organization approved successfully.",
                "organization": {
                    "id": organization.id,
                    "name": organization.name,
                    "status": organization.status,
                },
            },
            status=status.HTTP_200_OK,
        )

class InvitationView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsOrganizationAdmin,
    ]

    def post(self, request, organization_id):
        serializer = OrganizationInvitationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        organization = Organization.objects.get(
            id=organization_id,
            status="APPROVED",
        )
        invitation = create_invitation(
            organization=organization,
            email=serializer.validated_data["email"],
            invited_by=request.user,
        )
        return Response(
            {
                "message": "Staff invitation created successfully.",
                "invitation": {
                    "id": str(invitation.id),
                    "email": invitation.email,
                    "expires_at": invitation.expires_at,
                    "status": invitation.status,
                },
            },
            status=status.HTTP_201_CREATED,
        )