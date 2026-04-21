import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer


class UserChatConsumer(AsyncWebsocketConsumer):
    """
    Single multiplexed WebSocket connection for a user.

    On connect, the user is automatically subscribed to the channel
    groups for every room they have joined — no need to open one
    connection per room.

    Send format (client → server):
        {
            "room_slug": "my-room",
            "content":   "Hello!",
            "channel":   "community",   // optional, default: community
            "parent_id": "<uuid>"        // optional, for replies
        }

    Receive format (server → client):
        {
            "id":         "<uuid>",
            "room_slug":  "my-room",
            "sender_id":  "<uuid>",
            "content":    "Hello!",
            "channel":    "community",
            "parent_id":  null,
            "attachment_url": "https://media.../file.jpg",
            "created_at": "2026-04-21T05:00:00+06:00"
        }
    """

    async def connect(self):
        user = self.scope.get("user")

        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        self.user = user

        # Subscribe to every room the user is a member of
        self.room_group_names = await self._get_user_room_groups(user)

        for group_name in self.room_group_names:
            await self.channel_layer.group_add(group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        for group_name in getattr(self, "room_group_names", []):
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            return

        room_slug = data.get("room_slug", "").strip()
        content = data.get("content", "").strip()
        channel = data.get("channel", "community")
        parent_id = data.get("parent_id")

        if not room_slug or not content:
            # For websocket only text is allowed, attachments come through HTTP
            return

        # Verify the user is actually a member of the requested room
        room = await self._get_joined_room(self.user, room_slug)
        if room is None:
            await self.send(text_data=json.dumps({
                "error": f"You are not a member of room '{room_slug}'."
            }))
            return

        parent = None
        if parent_id:
            parent = await self._get_message(parent_id)

        message = await self._create_message(
            user=self.user,
            room=room,
            content=content,
            channel=channel,
            parent=parent,
        )

        group_name = f"room_{room_slug}"
        await self.channel_layer.group_send(
            group_name,
            {
                "type": "chat_message",
                "data": {
                    "id": str(message.id),
                    "room_slug": room_slug,
                    "sender_id": str(self.user.id),
                    "content": message.content,
                    "channel": message.channel,
                    "parent_id": str(message.parent_id) if message.parent_id else None,
                    "attachment_url": None, # WebSockets only do text for us
                    "created_at": message.created_at.isoformat(),
                }
            }
        )

    async def chat_message(self, event):
        """Receive a message from any subscribed room group and forward to client."""
        await self.send(text_data=json.dumps(event["data"]))

    # ─────────────────────────── ORM helpers ───────────────────────────

    @database_sync_to_async
    def _get_user_room_groups(self, user):
        from app.community.model.membership import RoomMembership
        slugs = RoomMembership.objects.filter(
            user=user
        ).values_list("room__slug", flat=True)
        return [f"room_{slug}" for slug in slugs]

    @database_sync_to_async
    def _get_joined_room(self, user, slug):
        from app.community.model.room import Room
        from app.community.model.membership import RoomMembership
        try:
            room = Room.objects.get(slug=slug, is_active=True)
            RoomMembership.objects.get(user=user, room=room)
            return room
        except (Room.DoesNotExist, RoomMembership.DoesNotExist):
            return None

    @database_sync_to_async
    def _get_message(self, message_id):
        from app.community.model.message import Message
        try:
            return Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def _create_message(self, *, user, room, content, channel, parent):
        from app.community.services.message_service import create_message
        return create_message(
            user=user,
            room=room,
            content=content,
            channel=channel,
            parent=parent,
        )
