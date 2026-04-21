from app.community.model.membership import RoomMembership
from app.community.model.message import Message


def get_joined_rooms_queryset(user):
    return (
        RoomMembership.objects
        .filter(user=user)
        .select_related(
            "room",
            "room__creator",
        )
        .order_by("room__name")
    )

def serialize_joined_rooms(memberships):
    """
    Takes an iterable of RoomMembership objects and formats them,
    performing a targeted query for the last announcement per room.
    """
    results = []
    for membership in memberships:
        room = membership.room

        last_announcement = (
            Message.objects
            .filter(room=room, channel=Message.Channel.ANNOUNCEMENT, is_active=True)
            .order_by("-created_at")
            .values("content", "created_at")
            .first()
        )

        results.append({
            "room_name": room.name,
            "room_slug": room.slug,
            "creator_name": room.creator.display_name,
            "last_announcement_content": last_announcement["content"] if last_announcement else None,
            "last_announcement_at": last_announcement["created_at"] if last_announcement else None,
        })

    return results
