from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser


@database_sync_to_async
def get_user_from_token(token: str):
    """Validate a JWT access token and return the corresponding user."""
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        from django.contrib.auth import get_user_model

        User = get_user_model()
        validated = AccessToken(token)
        return User.objects.get(id=validated["user_id"])
    except Exception:
        return AnonymousUser()


class JwtAuthMiddleware:
    """
    Channels middleware that reads a JWT token from the WebSocket
    query string and populates scope["user"].

    Client connects with:
        ws://host/ws/rooms/slug/?token=<access_token>
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token_list = params.get("token", [])

        if token_list:
            scope["user"] = await get_user_from_token(token_list[0])
        else:
            scope["user"] = AnonymousUser()

        return await self.inner(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    """Drop-in replacement for AuthMiddlewareStack that uses JWT."""
    return JwtAuthMiddleware(inner)
