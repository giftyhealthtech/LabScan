from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .services import create_tokens
from .serializers import LoginSerializer
        
class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        membership = serializer.validated_data["membership"]

        tokens = create_tokens(user)

        response = {
            **tokens,
            "user": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
        }

        if membership:
            response["organization"] = {
                "id": membership.organization.id,
                "name": membership.organization.name,
                "role": membership.role,
            }
        else:
            response["platform_admin"] = True

        return Response(response, status=status.HTTP_200_OK)
