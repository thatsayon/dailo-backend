from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task(bind=True, max_retries=3, default_retry_delay=10)
def send_otp_email(self, recipient_email: str, full_name: str, otp: str):
    """Send OTP verification email in the background."""
    subject = "Your Dailo Verification Code"
    first_name = full_name.split()[0] if full_name else "there"
    message = (
        f"Hi {first_name},\n\n"
        f"Your verification code is: {otp}\n\n"
        f"This code expires in 10 minutes. Do not share it with anyone.\n\n"
        f"— The Dailo Team"
    )
    html_message = f"""
    <div style="font-family:Arial,sans-serif;max-width:480px;margin:auto;padding:32px;background:#f9f9f9;border-radius:8px">
      <h2 style="color:#1a1a1a">Verify your Dailo account</h2>
      <p style="color:#444">Hi <strong>{first_name}</strong>,</p>
      <p style="color:#444">Use the code below to verify your account. It expires in <strong>10 minutes</strong>.</p>
      <div style="font-size:36px;font-weight:bold;letter-spacing:12px;text-align:center;
                  padding:24px;background:#fff;border-radius:8px;margin:24px 0;color:#1a1a1a">
        {otp}
      </div>
      <p style="color:#999;font-size:12px">If you didn't create a Dailo account, you can ignore this email.</p>
    </div>
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
    except Exception as exc:
        raise self.retry(exc=exc)
