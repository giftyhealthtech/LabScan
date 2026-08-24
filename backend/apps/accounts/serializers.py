from .models import User
from .services import create_user

from rest_framework import serializers
        
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
    