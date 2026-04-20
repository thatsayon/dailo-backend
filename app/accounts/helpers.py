import random
from django.utils import timezone
from datetime import timedelta


def _first_error(serializer) -> str:
    """Extract the first human-readable error from serializer.errors."""
    for field, messages in serializer.errors.items():
        msg = str(messages[0]) if isinstance(messages, list) and messages else str(messages)
        if field == "non_field_errors":
            return msg
        return f"{field}: {msg}"
    return "invalid data."


def _generate_otp() -> str:
    """Return a cryptographically random 6-digit OTP string."""
    return f"{random.SystemRandom().randint(0, 999999):06d}"


def _create_otp_record(user, purpose=None):
    """Invalidate old unused OTPs for this user+purpose, then create a fresh one.
    Returns (OTPVerification instance, raw_otp string).
    """
    from app.accounts.models import OTPVerification  # local import to avoid circular deps

    if purpose is None:
        purpose = OTPVerification.Purpose.REGISTRATION

    OTPVerification.objects.filter(
        user=user, purpose=purpose, is_used=False
    ).update(is_used=True)

    raw_otp = _generate_otp()
    otp_obj = OTPVerification(
        user=user,
        purpose=purpose,
        expires_at=timezone.now() + timedelta(minutes=10),
    )
    otp_obj.set_otp(raw_otp)
    otp_obj.save()
    return otp_obj, raw_otp
