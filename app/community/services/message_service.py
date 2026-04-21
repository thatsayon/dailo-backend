from app.community.models import Message

from app.notification.services.notification_service import notify_room_members


def create_message(
    *,
    user,
    room,
    content,
    channel,
    parent=None
):
    message = Message.objects.create(
        sender=user,
        room=room,
        content=content,
        channel=channel,
        parent=parent
    )

    notify_room_members(
        room=room,
        message=message
    )

    return message
