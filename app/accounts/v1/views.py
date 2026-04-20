from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.contrib.auth import authenticate

from app.accounts.models import UserAccount, OTPVerification
from app.accounts.tokens import get_tokens_for_user
from app.accounts.helpers import _first_error, _generate_otp, _create_otp_record
from app.accounts.tasks import send_otp_email

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    VerifyOTPSerializer,
    ResendOTPSerializer,
)



class RegisterView(APIView):
    """Register a new user — sends OTP by email; account activates after verification.
    If an unverified account already exists for the email, it is updated and a fresh OTP is sent.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": _first_error(serializer)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        full_name = serializer.validated_data["full_name"]
        password = serializer.validated_data["password"]

        existing = UserAccount.objects.filter(email=email, is_active=False).first()
        if existing:
            # Update the unverified account in-place (keep username, id, etc.)
            existing.full_name = full_name
            existing.set_password(password)
            existing.save(update_fields=["full_name", "password"])
            user = existing
        else:
            user = UserAccount.objects.create_user(
                email=email,
                password=password,
                full_name=full_name,
                is_active=False,  # explicit — manager defaults to True via setdefault
            )

        otp_obj, raw_otp = _create_otp_record(user)
        print(raw_otp)

        # Fire-and-forget — background task
        send_otp_email.delay(user.email, user.full_name, raw_otp)

        return Response(
            {
                "success": True,
                "otp_token": str(otp_obj.token),
                "message": "Registration successful. Please check your email for the OTP to verify your account.",
            },
            status=status.HTTP_201_CREATED,
        )


class VerifyOTPView(APIView):
    """Verify the OTP to activate the account and receive JWT tokens."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": _first_error(serializer)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = serializer.validated_data["token"]
        raw_otp = serializer.validated_data["otp"]

        try:
            otp_obj = OTPVerification.objects.select_related("user").get(
                token=token,
                purpose=OTPVerification.Purpose.REGISTRATION,
            )
        except OTPVerification.DoesNotExist:
            return Response(
                {"error": "Invalid verification token."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp_obj.is_used:
            return Response(
                {"error": "This OTP has already been used."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if otp_obj.is_expired:
            return Response(
                {"error": "OTP has expired. Please request a new one."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not otp_obj.check_otp(raw_otp):
            return Response(
                {"error": "Invalid OTP."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Activate user
        user = otp_obj.user
        user.is_active = True
        user.save(update_fields=["is_active"])

        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "success": True,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                },
            },
            status=status.HTTP_200_OK,
        )


class ResendRegistrationOTPView(APIView):
    """Resend the registration OTP for an unverified account."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": _first_error(serializer)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]

        try:
            user = UserAccount.objects.get(email=email, is_active=False)
        except UserAccount.DoesNotExist:
            # Deliberately vague to avoid user enumeration
            return Response(
                {"error": "No unverified account found with this email."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_obj, raw_otp = _create_otp_record(user)
        send_otp_email.delay(user.email, user.full_name, raw_otp)

        return Response(
            {
                "success": True,
                "otp_token": str(otp_obj.token),
                "message": "A new OTP has been sent to your email.",
            },
            status=status.HTTP_200_OK,
        )


class LoginView(APIView):
    """Authenticate with email + password; returns JWT pair + user info."""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": _first_error(serializer)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(
            username=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if not user:
            return Response(
                {"error": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {"error": "Account is not verified. Please verify your email first."},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = get_tokens_for_user(user)

        return Response(
            {
                "success": True,
                "access_token": tokens["access"],
                "refresh_token": tokens["refresh"],
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "username": user.username,
                    "full_name": user.full_name,
                },
            },
            status=status.HTTP_200_OK,
        )
