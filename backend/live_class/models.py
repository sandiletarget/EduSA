from django.conf import settings
from django.db import models

from backend.models import LiveClassSession


class LiveClass(LiveClassSession):
    """Proxy model for readability in AI modules."""

    class Meta:
        proxy = True
        verbose_name = "Live Class"
        verbose_name_plural = "Live Classes"


class TranscriptSegment(models.Model):
    live_class = models.ForeignKey(
        LiveClassSession,
        on_delete=models.CASCADE,
        related_name="transcript_segments",
    )
    speaker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transcript_segments",
    )
    text = models.TextField()
    start_time = models.FloatField(default=0.0)
    end_time = models.FloatField(default=0.0)
    is_flagged = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.live_class} @ {self.start_time}s"


class AISummary(models.Model):
    live_class = models.ForeignKey(
        LiveClassSession,
        on_delete=models.CASCADE,
        related_name="ai_summaries",
    )
    content = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Summary for {self.live_class}"


class AIQuestion(models.Model):
    STATUS_SUGGESTED = "suggested"
    STATUS_ANSWERED = "answered"
    STATUS_FLAGGED = "flagged"

    STATUS_CHOICES = (
        (STATUS_SUGGESTED, "Suggested"),
        (STATUS_ANSWERED, "Answered"),
        (STATUS_FLAGGED, "Flagged"),
    )

    live_class = models.ForeignKey(
        LiveClassSession,
        on_delete=models.CASCADE,
        related_name="ai_questions",
    )
    question = models.TextField()
    answer = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUGGESTED)
    asked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_questions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AI Question ({self.status})"


class AIInsight(models.Model):
    INSIGHT_PARTICIPATION = "participation"
    INSIGHT_ATTENDANCE = "attendance"
    INSIGHT_MODERATION = "moderation"

    INSIGHT_CHOICES = (
        (INSIGHT_PARTICIPATION, "Participation"),
        (INSIGHT_ATTENDANCE, "Attendance"),
        (INSIGHT_MODERATION, "Moderation"),
    )

    live_class = models.ForeignKey(
        LiveClassSession,
        on_delete=models.CASCADE,
        related_name="ai_insights",
    )
    insight_type = models.CharField(max_length=20, choices=INSIGHT_CHOICES)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Insight ({self.insight_type})"
