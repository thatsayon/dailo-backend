from rest_framework.response import Response
from rest_framework import generics, permissions

from django.shortcuts import get_object_or_404
from app.community.model.room import Room
from app.community.model.message import Message
from app.community.model.membership import RoomMembership
from app.community.services.membership_service import join_room
from app.community.services.room_service import get_joined_rooms_queryset, serialize_joined_rooms
from app.community.services.message_service import create_message, broadcast_message
from app.community.v1.serializers import MessageUploadSerializer

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


class JoinedRoomsListView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        queryset = get_joined_rooms_queryset(user=request.user)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            data = serialize_joined_rooms(page)
            return self.get_paginated_response(data)

        data = serialize_joined_rooms(queryset)
        return Response(data)

class MessageUploadAPIView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageUploadSerializer

    def post(self, request, slug):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        room = get_object_or_404(Room, slug=slug, is_active=True)

        # check membership
        if not RoomMembership.objects.filter(user=user, room=room).exists():
            return Response(
                {"error": "You must join the room before sending messages."},
                status=403
            )

        parent = None
        parent_id = serializer.validated_data.get("parent_id")
        if parent_id:
            parent = get_object_or_404(Message, id=parent_id)

        # save message & upload to cloud storage
        message = create_message(
            user=user,
            room=room,
            content=serializer.validated_data.get("content", ""),
            channel=serializer.validated_data.get("channel"),
            parent=parent,
            attachment=serializer.validated_data.get("attachment")
        )

        # broadcast to websocket clients
        broadcast_message(message)

        return Response({
            "success": True,
            "message_id": message.id
        })
