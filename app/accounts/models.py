from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db import models
from cloudinary.models import CloudinaryField
from core.models import BaseModel


class CustomAccountManager(BaseUserManager):
    def normalize_email_strict(self, email: str) -> str:
        email = self.normalize_email(email)
        local, domain = email.split("@")
        return f"{local.lower()}@{domain}".strip()

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_("Email must be provided"))
        email = self.normalize_email_strict(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password) if password else user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserAccount.Role.ADMIN)
        if not extra_fields["is_staff"]:
            raise ValueError(_("Superuser must have is_staff=True"))
        if not extra_fields["is_superuser"]:
            raise ValueError(_("Superuser must have is_superuser=True"))
        return self.create_user(email, password, **extra_fields)


class UserAccount(AbstractBaseUser, PermissionsMixin, BaseModel):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        USER = "user", "User"
        CREATOR = "creator", "Creator"

    class AuthProvider(models.TextChoices):
        EMAIL = "email", "Email"
        GOOGLE = "google", "Google"

    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(max_length=80, blank=True, default="")
    username = models.CharField(max_length=50, unique=True, null=True, blank=True)

    profile_pic = CloudinaryField(blank=True, null=True)
    profile_updated_at = models.DateTimeField(blank=True, null=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        db_index=True,
    )
    auth_provider = models.CharField(
        max_length=20,
        choices=AuthProvider.choices,
        default=AuthProvider.EMAIL,
    )
    provider_uid = models.CharField(max_length=255, blank=True, null=True, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomAccountManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["auth_provider"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["auth_provider", "provider_uid"],
                name="unique_provider_user",
                condition=models.Q(provider_uid__isnull=False),
            )
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._original_profile_pic = self.profile_pic

    def clean(self):
        if self.auth_provider == self.AuthProvider.EMAIL and self.provider_uid:
            raise ValidationError(_("Email users should not have a provider_uid."))
        if self.auth_provider != self.AuthProvider.EMAIL and not self.provider_uid:
            raise ValidationError(_("OAuth users must have a provider_uid."))

    def save(self, *args, **kwargs):
        if self.profile_pic != self._original_profile_pic:
            self.profile_updated_at = timezone.now()
            self._original_profile_pic = self.profile_pic
        super().save(*args, **kwargs)

    @property
    def display_name(self) -> str:
        return self.full_name or self.username or self.email.split("@")[0]

    @property
    def avatar_url(self) -> str | None:
        return self.profile_pic.url if self.profile_pic else None

    def __str__(self) -> str:
        return self.email

    def __repr__(self) -> str:
        return f"<UserAccount id={self.pk} email={self.email!r}>"
