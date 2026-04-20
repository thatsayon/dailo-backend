from rest_framework import serializers

from app.creator.models import CreatorApplication


class CreatorApplicationListSerializer(serializers.ModelSerializer):
    email = serializers.CharField(
        source="user.email",
        read_only=True
    )

    class Meta:
        model = CreatorApplication
        fields = [
            "id",
            "display_name",
            "email",
            "mobile_number",
            "primary_platform_link",
            "status",
            "created_at",
            "reviewed_at",
        ]


class CreatorApplicationStatusSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=CreatorApplication.Status.choices
    )
    admin_note = serializers.CharField(
        required=False,
        allow_blank=True
    )
