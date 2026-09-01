from rest_framework import serializers

from apps.accounts.serializers import UserSerializer
from .models import Organization
from .services import register_organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "name",
            "email",
            "phone",
            "state",
            "address",
        ]


class OrganizationRegistrationSerializer(serializers.Serializer):
    organization = OrganizationSerializer()
    admin = UserSerializer()

    def create(self, validated_data):
        return register_organization(
            organization_data=validated_data["organization"],
            admin_data=validated_data["admin"],
        )
        
class OrganizationApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = [
            "id",
            "name",
            "email",
            "phone",
            "state",
            "address",
            "status",
            "created_at",
        ]
        read_only_fields = fields

class OrganizationRejectSerializer(serializers.Serializer):
    rejection_reason = serializers.CharField(
        required=True,
        allow_blank=False,
    )
class OrganizationInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        return value.lower().strip()  

class InvitationAcceptSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
    )

    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
    )

    def validate(self, attrs):
        if attrs["password_confirm"] != attrs["password"]:
            raise serializers.ValidationError({
                "password_confirm": "Passwords do not match."
            })

        return attrs