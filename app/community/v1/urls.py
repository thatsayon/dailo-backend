from django.urls import path

from .views import JoinRoomAPIView, JoinedRoomsListView, MessageUploadAPIView

urlpatterns = [
    path(
        "rooms/",
        JoinedRoomsListView.as_view(),
        name="joined-rooms-list"
    ),
    path(
        "rooms/<slug:slug>/join/",
        JoinRoomAPIView.as_view(),
        name="join-room"
    ),
    path(
        "rooms/<slug:slug>/messages/upload/",
        MessageUploadAPIView.as_view(),
        name="message-upload"
    ),
]
