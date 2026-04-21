from django.urls import path

from .views import JoinRoomAPIView

urlpatterns = [
    path(
        "rooms/<slug:slug>/join/",
        JoinRoomAPIView.as_view(),
        name="Join Room"
    )
]
