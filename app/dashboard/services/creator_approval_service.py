# app/creator/services/creator_approval_service.py

from django.utils.text import slugify
from django.utils import timezone

from app.creator.models import CreatorApplication, CreatorProfile
from app.community.models import Room
from app.accounts.models import UserAccount
from app.community.services.membership_service import join_room


def generate_unique_slug(base_slug: str):
    slug = base_slug
    counter = 1

    while Room.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug



def update_creator_application_status(
    *,
    application: CreatorApplication,
    status: str,
    admin_note: str = ""
):
    application.status = status
    application.admin_note = admin_note
    application.reviewed_at = timezone.now()

    application.save(update_fields=[
        "status",
        "admin_note",
        "reviewed_at",
    ])

    # approved flow
    if status == CreatorApplication.Status.APPROVED:

        # create creator profile
        profile, _ = CreatorProfile.objects.get_or_create(
            user=application.user,
            defaults={
                "display_name": application.display_name,
            }
        )

        # update user role
        application.user.role = UserAccount.Role.CREATOR
        application.user.save(update_fields=["role"])

        # auto create room
        base_slug = slugify(application.display_name)
        slug = generate_unique_slug(base_slug)

        room, _ = Room.objects.get_or_create(
            creator=profile,
            defaults={
                "name": application.display_name,
                "slug": slug,
                "description": "",
                "price_monthly": 0,
            }
        )

        # auto join the creator to their own room
        join_room(user=application.user, room=room)

    return application
