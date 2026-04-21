import os

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    'config.settings.dev'
)

# django.setup() is called inside get_asgi_application().
# ALL model / routing imports MUST come after this line.
from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from config.ws_middleware import JwtAuthMiddlewareStack
from config.websocket_routes import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
