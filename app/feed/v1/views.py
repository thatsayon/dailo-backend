from rest_framework.generics import ListAPIView
from rest_framework import permissions

from app.feed.v1.serializers import FeedRoomSerializer
from app.feed.selectors.room_selector import get_active_rooms

class FeedRoomListAPIView(ListAPIView):
    serializer_class = FeedRoomSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return get_active_rooms()
