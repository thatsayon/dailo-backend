from app.community.models import Room


def get_active_rooms():
    return Room.objects.select_related(
        "creator",
        "creator__user"
    ).filter(
        is_active=True
    ).order_by(
        "-created_at"
    )
