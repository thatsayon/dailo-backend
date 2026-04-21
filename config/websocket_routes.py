from app.community.realtime.routing import websocket_urlpatterns as community_ws

from app.notification.realtime.routing import websocket_urlpatterns as notification_ws


websocket_urlpatterns = [
    *community_ws,
    *notification_ws,
]
