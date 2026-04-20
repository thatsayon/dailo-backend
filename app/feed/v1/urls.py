from django.urls import path

from .views import FeedRoomListAPIView

urlpatterns = [
    path(
        "",
        FeedRoomListAPIView.as_view(),
        name="feed-rooms"
    ),
]
