from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from .services import (
    create_invitation,
    accept_invitation,
    validate_invitation,
) 
from .models import (
    Organization, 
    OrganizationMembership,
    OrganizationInvitation
)
from .permissions import (
    IsPlatformAdmin,
    IsOrganizationAdmin,
)
from .serializers import (
    OrganizationRegistrationSerializer,
    OrganizationApprovalSerializer,
    OrganizationInvitationSerializer,
    InvitationAcceptSerializer
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
        # organization = get_object_or_404(
        #     Organization,
        #     id=organization_id,
        #     status="APPROVED",
        # )

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
        

class AcceptInvitationView(APIView):

    def post(self, request, invitation_token):
        if request.user.is_authenticated:

            try:
                user, membership = accept_invitation(
                    invitation_token=invitation_token,
                    authenticated_user=request.user,
                )

            except ValueError as exc:
                return Response(
                    {
                        "detail": str(exc)
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(
                {
                    "message": "Invitation accepted successfully.",

                    "user": {
                        "id": user.id,
                        "email": user.email,
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "phone": user.phone,
                    },

                    "organization": {
                        "id": membership.organization.id,
                        "name": membership.organization.name,
                        "role": membership.role,
                    },
                },
                status=status.HTTP_200_OK,
            )

        serializer = InvitationAcceptSerializer (data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user, membership = accept_invitation(
                invitation_token=invitation_token,
                first_name=serializer.validated_data["first_name"],
                last_name=serializer.validated_data["last_name"],
                phone=serializer.validated_data.get("phone", "",),
                password=serializer.validated_data["password"],
            )

        except ValueError as exc:
            return Response(
                {
                    "detail": str(exc)
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate JWT
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Staff account created successfully.",

                "access": str(
                    refresh.access_token
                ),

                "refresh": str(refresh),

                "user": {
                    "id": user.id,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "phone": user.phone,
                },

                "organization": {
                    "id": membership.organization.id,
                    "name": membership.organization.name,
                    "role": membership.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )