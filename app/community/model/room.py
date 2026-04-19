from django.db import models
from django.utils.text import slugify

from core.models import BaseModel


class Room(BaseModel):
    creator = models.OneToOneField(
        "creator.CreatorProfile",
        on_delete=models.CASCADE,
        related_name="room"
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    cover_image = models.ImageField(
        upload_to="rooms/covers/",
        null=True,
        blank=True
    )

    price_monthly = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0
    )

    currency = models.CharField(max_length=10, default="BDT")
    member_count = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
