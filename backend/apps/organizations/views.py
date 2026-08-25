from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated


from .models import Organization
from .permissions import IsPlatformAdmin
from .serializers import (
    OrganizationRegistrationSerializer,
    OrganizationApprovalSerializer,
    OrganizationRejectSerializer,
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
        # organization.rejection_reason = ""
        organization.save(
            update_fields=[
                "status",
                # "rejection_reason",
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
