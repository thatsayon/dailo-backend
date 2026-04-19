from django.db import models
from django.utils import timezone

from core.models import BaseModel

class CreatorApplication(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        UNDER_REVIEW = "under_review", "Under review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        "accounts.UserAccount",
        on_delete=models.CASCADE,
        related_name="creator_application"
    )

    display_name = models.CharField(
        max_length=120
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        db_index=True
    )

    admin_note = models.TextField(blank=True)

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def approve(self):
        self.status = self.Status.APPROVED
        self.reviewed_at = timezone.now()

        self.save(update_fields=[
            "status",
            "reviewed_at",
        ])

    def reject(self, reason=""):
        self.status = self.Status.REJECTED
        self.admin_note = reason
        self.reviewed_at = timezone.now()

        self.save(update_fields=[
            "status",
            "admin_note",
            "reviewed_at",
        ])

    def __str__(self):
        return f"{self.display_name} ({self.user.email})"



class CreatorProfile(BaseModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        SUSPENDED = "suspended", "Suspended"

    user = models.OneToOneField(
        "accounts.UserAccount",
        on_delete=models.CASCADE,
        related_name="creator_profile"
    )

    display_name = models.CharField(max_length=120)
    bio = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    is_verified = models.BooleanField(
        default=False,
        help_text="manual verification badge"
    )

    last_active_at = models.DateTimeField(
        null=True,
        blank=True
    )

    def __str__(self):
        return self.display_name



class CreatorLink(BaseModel):
    class Platform(models.TextChoices):
        YOUTUBE = "youtube", "YouTube"
        FACEBOOK = "facebook", "Facebook"
        INSTAGRAM = "instagram", "Instagram"
        TWITTER = "twitter", "Twitter"
        TIKTOK = "tiktok", "TikTok"
        LINKEDIN = "linkedin", "LinkedIn"
        GITHUB = "github", "GitHub"
        WEBSITE = "website", "Website"
        OTHER = "other", "Other"

    creator = models.ForeignKey(
        CreatorProfile,
        on_delete=models.CASCADE,
        related_name="links"
    )

    platform = models.CharField(
        max_length=50,
        choices=Platform.choices
    )

    url = models.URLField()

    follower_count = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    is_primary = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=["platform"]),
        ]

    def __str__(self):
        return self.url
