from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from app.community.models import Message

from app.notification.services.notification_service import notify_room_members


def create_message(
    *,
    user,
    room,
    content="",
    channel,
    parent=None,
    attachment=None
):
    message = Message.objects.create(
        sender=user,
        room=room,
        content=content,
        channel=channel,
        parent=parent,
        attachment=attachment
    )

    notify_room_members(
        room=room,
        message=message
    )

    return message


def broadcast_message(message):
    """
    Broadcasts a saved message to the channels group for its room.
    Safe to call from sync code (e.g. Django views).
    """
    channel_layer = get_channel_layer()
    group_name = f"room_{message.room.slug}"

    payload = {
        "id": str(message.id),
        "room_slug": message.room.slug,
        "sender_id": str(message.sender_id),
        "content": message.content,
        "channel": message.channel,
        "parent_id": str(message.parent_id) if message.parent_id else None,
        "attachment_url": message.attachment.url if message.attachment else None,
        "created_at": message.created_at.isoformat(),
    }

    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "chat_message",
            "data": payload
        }
    )
