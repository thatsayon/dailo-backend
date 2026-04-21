from django.db import models

from core.models import BaseModel

class RoomMembership(BaseModel):
    user = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.CASCADE,
        related_name="room_memberships"
    )
    room = models.ForeignKey(
        "community.Room",
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "room")
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["room"]),
        ]

    def __str__(self):
        return f"{self.user.email} joined {self.room.name}"
