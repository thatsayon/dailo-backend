from django.db import transaction

from app.community.model.membership import RoomMembership


@transaction.atomic
def join_room(*, user, room):
    membership, created = RoomMembership.objects.get_or_create(
        user=user,
        room=room
    )

    if created:
        room.member_count += 1
        room.save(update_fields=["member_count"])

    return membership, created
