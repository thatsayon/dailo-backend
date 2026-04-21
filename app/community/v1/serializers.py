from rest_framework import serializers

from app.community.models import Message

class MessageUploadSerializer(serializers.Serializer):
    content = serializers.CharField(required=False, allow_blank=True)
    channel = serializers.ChoiceField(
        choices=Message.Channel.choices,
        default=Message.Channel.COMMUNITY
    )
    parent_id = serializers.UUIDField(required=False, allow_null=True)
    attachment = serializers.FileField(required=True)

    def validate(self, attrs):
        # We enforce at least the attachment to be present, which is guaranteed by required=True
        return attrs
