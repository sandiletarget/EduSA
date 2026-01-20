import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from classes.models import Class, ClassMembership
from .models import LiveClassSession, LiveParticipant


class LiveClassConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or isinstance(user, AnonymousUser) or not user.is_authenticated:
            await self.close()
            return

        self.class_id = self.scope["url_route"]["kwargs"]["class_id"]
        allowed = await self._user_allowed(user, self.class_id)
        if not allowed:
            await self.close()
            return

        self.room_group_name = f"live_class_{self.class_id}"
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        await self._ensure_participant(user)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "broadcast",
                "payload": {
                    "event": "join",
                    "user": user.username,
                },
            },
        )

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event = content.get("event")

        if event in {"offer", "answer", "ice", "chat"}:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast",
                    "payload": content,
                },
            )
        elif event in {"raise_hand", "mute_all", "lock_class", "end_class", "start_class"}:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "broadcast",
                    "payload": content,
                },
            )

    async def broadcast(self, event):
        await self.send_json(event["payload"])

    @database_sync_to_async
    def _user_allowed(self, user, class_id):
        classroom = Class.objects.filter(pk=class_id).first()
        if not classroom:
            return False
        if user == classroom.teacher:
            return True
        return ClassMembership.objects.filter(classroom=classroom, learner=user).exists()

    @database_sync_to_async
    def _ensure_participant(self, user):
        classroom = Class.objects.get(pk=self.class_id)
        session, _ = LiveClassSession.objects.get_or_create(
            classroom=classroom,
            teacher=classroom.teacher,
            defaults={"status": LiveClassSession.STATUS_LIVE, "started_at": timezone.now()},
        )
        LiveParticipant.objects.get_or_create(session=session, user=user)
        session.participants.add(user)
