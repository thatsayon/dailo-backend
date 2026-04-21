from rest_framework.response import Response

from rest_framework import generics, permissions

from app.community.model.room import Room

from app.community.services.membership_service import join_room

class JoinRoomAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        room = Room.objects.get(
            slug=slug,
            is_active=True
        )

        membership, created = join_room(
            user=request.user,
            room=room
        )

        return Response({
            "joined": created,
            "room": room.slug,
            "member_count": room.member_count
        })
