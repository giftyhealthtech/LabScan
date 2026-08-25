from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import OrganizationRegistrationSerializer

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
