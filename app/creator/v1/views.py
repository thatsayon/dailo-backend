from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from app.accounts.models import UserAccount
from app.creator.models import CreatorApplication
from app.accounts.helpers import _first_error, _create_otp_record
from app.accounts.tasks import send_otp_email

from .serializers import CreatorRegisterSerializer


class CreatorRegisterView(APIView):
    """
    Register a new creator.
    Creates an inactive user and a pending CreatorApplication, then sends OTP.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = CreatorRegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": _first_error(serializer)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        data = serializer.validated_data
        email = data["email"]
        full_name = data["full_name"]
        password = data["password"]

        # 1. Upsert UserAccount (like regular registration)
        existing_user = UserAccount.objects.filter(email=email, is_active=False).first()
        if existing_user:
            existing_user.full_name = full_name
            existing_user.set_password(password)
            existing_user.role = UserAccount.Role.CREATOR
            existing_user.save(update_fields=["full_name", "password", "role"])
            user = existing_user
        else:
            user = UserAccount.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                role=UserAccount.Role.CREATOR,
                is_active=False,
            )

        # 2. Upsert CreatorApplication
        CreatorApplication.objects.update_or_create(
            user=user,
            defaults={
                "display_name": data["display_name"],
                "mobile_number": data.get("mobile_number", ""),
                "whatsapp_number": data.get("whatsapp_number", ""),
                "primary_platform_link": data.get("primary_platform_link", ""),
                "selfie": data.get("selfie"),
                "status": CreatorApplication.Status.PENDING,
            }
        )

        # 3. Create OTP and send email
        otp_obj, raw_otp = _create_otp_record(user)
        send_otp_email.delay(user.email, user.full_name, raw_otp)

        return Response(
            {
                "success": True,
                "otp_token": str(otp_obj.token),
                "message": "Creator registration successful. Please check your email for the OTP to verify your account.",
            },
            status=status.HTTP_201_CREATED,
        )
