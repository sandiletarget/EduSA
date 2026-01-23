"""Celery tasks for async AI processing."""
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from backend.ai.services import build_summary, suggest_answer, detect_flags
from backend.live_class.models import TranscriptSegment, AISummary, AIQuestion, AIInsight


def _push_ai_event(live_class_id, payload):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"ai_class_{live_class_id}",
        {"type": "ai_message", "payload": payload},
    )


@shared_task
def process_transcript_segment(segment_id):
    segment = TranscriptSegment.objects.get(id=segment_id)
    flagged, reason = detect_flags(segment.text)
    if flagged:
        segment.is_flagged = True
        segment.flag_reason = reason
        segment.save(update_fields=["is_flagged", "flag_reason"])
        AIInsight.objects.create(
            live_class=segment.live_class,
            insight_type=AIInsight.INSIGHT_MODERATION,
            content=f"Flagged language detected: {reason}",
        )
        _push_ai_event(segment.live_class_id, {
            "event": "moderation_alert",
            "message": reason,
        })


@shared_task
def generate_summary(live_class_id):
    content = build_summary(live_class_id)
    summary = AISummary.objects.create(live_class_id=live_class_id, content=content)
    _push_ai_event(live_class_id, {
        "event": "summary_ready",
        "summary": summary.content,
    })


@shared_task
def answer_question(question_id):
    ai_question = AIQuestion.objects.get(id=question_id)
    transcript = TranscriptSegment.objects.filter(live_class=ai_question.live_class).values_list("text", flat=True)[:5]
    ai_question.answer = suggest_answer(ai_question.question, list(transcript))
    ai_question.status = AIQuestion.STATUS_ANSWERED
    ai_question.save(update_fields=["answer", "status"])
    _push_ai_event(ai_question.live_class_id, {
        "event": "ai_answer",
        "question": ai_question.question,
        "answer": ai_question.answer,
    })
