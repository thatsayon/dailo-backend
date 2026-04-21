from asgiref.sync import async_to_sync

from channels.layers import get_channel_layer

from app.notification.models import Notification

from app.community.models import RoomMembership


def notify_room_members(*, room, message):
    memberships = RoomMembership.objects.filter(
        room=room
    ).select_related("user")

    channel_layer = get_channel_layer()

    for membership in memberships:
        user = membership.user

        Notification.objects.create(
            user=user,
            title=f"New message in {room.name}",
            data={
                "room": room.slug,
                "message_id": str(message.id)
            }
        )

        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "data": {
                    "room": room.slug,
                    "message": message.content,
                }
            }
        )
