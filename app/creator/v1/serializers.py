from rest_framework import serializers
from app.accounts.models import UserAccount


class CreatorRegisterSerializer(serializers.Serializer):
    # --- User fields ---
    full_name = serializers.CharField(max_length=80)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)

    # --- CreatorApplication fields ---
    display_name = serializers.CharField(max_length=120)
    mobile_number = serializers.CharField(max_length=20)
    whatsapp_number = serializers.CharField(max_length=20)
    primary_platform_link = serializers.URLField()
    selfie = serializers.ImageField()

    def validate_email(self, value):
        value = value.lower().strip()
        user = UserAccount.objects.filter(email=value).first()
        if user and user.is_active:
            raise serializers.ValidationError("An account with this email already exists.")
        return value

    def validate_full_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Full name cannot be blank.")
        return value

    def validate_display_name(self, value):
        value = value.strip()
        if not value:
            raise serializers.ValidationError("Display name cannot be blank.")
        return value
