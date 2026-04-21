from django.db import models

from core.models import BaseModel


class Message(BaseModel):
    class Channel(models.TextChoices):
        ANNOUNCEMENT = "announcement", "Announcement"
        COMMUNITY = "community", "Community"

    room = models.ForeignKey(
        "community.Room",
        on_delete=models.CASCADE,
        related_name="messages"
    )
    sender = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    # message content
    content = models.TextField(blank=True)

    # image/file support (stored in R2 via your MediaStorage)
    attachment = models.FileField(
        upload_to="messages/files/",
        null=True,
        blank=True
    )

    # announcement or community chat
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        default=Channel.COMMUNITY,
        db_index=True
    )

    # reply system
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies"
    )


    # moderation support
    is_active = models.BooleanField(default=True)
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["room"]),
            models.Index(fields=["channel"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["parent"]),
        ]

    def __str__(self):
        return f"{self.room.slug} | {self.sender_id}"
