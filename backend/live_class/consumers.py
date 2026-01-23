import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone

from classes.models import Class, ClassMembership
from backend.models import LiveClassSession
from backend.live_class.models import TranscriptSegment, AIQuestion
from backend.ai.tasks import process_transcript_segment, answer_question


class AIClassConsumer(AsyncJsonWebsocketConsumer):
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

        self.room_group = f"ai_class_{self.class_id}"
        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group, self.channel_name)

    async def receive_json(self, content, **kwargs):
        event = content.get("event")

        if event == "transcript" and content.get("text"):
            await self._store_transcript(content)
        elif event == "question" and content.get("question"):
            await self._store_question(content)
        elif event == "toggle_ai" and content.get("enabled") is not None:
            await self._toggle_ai(content)

    async def ai_message(self, event):
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
    def _get_session(self):
        classroom = Class.objects.get(pk=self.class_id)
        session, _ = LiveClassSession.objects.get_or_create(
            classroom=classroom,
            teacher=classroom.teacher,
            defaults={"status": LiveClassSession.STATUS_LIVE, "started_at": timezone.now()},
        )
        return session

    async def _store_transcript(self, content):
        session = await self._get_session()
        segment = await database_sync_to_async(TranscriptSegment.objects.create)(
            live_class=session,
            speaker=self.scope.get("user"),
            text=content.get("text"),
            start_time=content.get("start", 0.0),
            end_time=content.get("end", 0.0),
        )
        process_transcript_segment.delay(segment.id)

    async def _store_question(self, content):
        session = await self._get_session()
        question = await database_sync_to_async(AIQuestion.objects.create)(
            live_class=session,
            question=content.get("question"),
            asked_by=self.scope.get("user"),
        )
        answer_question.delay(question.id)

    async def _toggle_ai(self, content):
        session = await self._get_session()
        enabled = bool(content.get("enabled"))
        session.ai_enabled = enabled
        await database_sync_to_async(session.save)(update_fields=["ai_enabled"])
        await self.channel_layer.group_send(
            self.room_group,
            {"type": "ai_message", "payload": {"event": "ai_toggle", "enabled": enabled}},
        )
