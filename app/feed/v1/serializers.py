from rest_framework import serializers

from app.community.models import Room

class FeedRoomSerializer(serializers.ModelSerializer):
    creator_name = serializers.CharField(
        source="creator.display_name",
        read_only=True
    )
    creator_username = serializers.CharField(
        source="creator.user.username",
        read_only=True
    )

    class Meta:
        model = Room
        fields = [
            "id",
            "name",
            "slug",
            "creator_name",
            "creator_username",
            "cover_image",
            "member_count",
            "price_monthly",
            "currency",
        ]
