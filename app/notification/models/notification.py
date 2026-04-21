from django.db import models

from core.models import BaseModel

class Notification(BaseModel):
    user = models.ForeignKey(
        "accounts.UserAccount",
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    data = models.JSONField(
        default=dict,
        blank=True
    )
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["is_read"]),
        ]
