from rest_framework import serializers

from .models import User
from .services import (
    create_user,
    login_user,
)
        
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
            "phone",
            "password",
        ]
        
    def validate_email(self, value):
        return value.lower().strip()

    def create(self, validated_data):
        return create_user(**validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        return value.lower().strip()

    def validate(self, attrs):
        result = login_user(
            email=attrs["email"],
            password=attrs["password"],
            request=self.context.get("request"),
        )

        attrs.update(result)
        return attrs