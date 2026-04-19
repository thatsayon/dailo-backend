from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, status

from django.contrib.auth import authenticate

from app.accounts.tokens import get_tokens_for_user
from app.accounts.helpers import _first_error

from .serializers import LoginSerializer

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
                {"error": "Account is not active."},
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
