from django.conf import settings
from django.db import models


class LiveClassSession(models.Model):
    STATUS_SCHEDULED = "scheduled"
    STATUS_LIVE = "live"
    STATUS_ENDED = "ended"

    STATUS_CHOICES = (
        (STATUS_SCHEDULED, "Scheduled"),
        (STATUS_LIVE, "Live"),
        (STATUS_ENDED, "Ended"),
    )

    classroom = models.ForeignKey(
        "classes.Class",
        on_delete=models.CASCADE,
        related_name="live_class_sessions",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hosted_live_classes",
    )
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="live_class_participations",
        blank=True,
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    ai_enabled = models.BooleanField(default=True)
    ai_mode = models.CharField(max_length=20, default="passive")
    chat_enabled = models.BooleanField(default=True)
    allow_student_drawing = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Live class for {self.classroom.name} ({self.status})"


class LiveParticipant(models.Model):
    session = models.ForeignKey(
        LiveClassSession,
        on_delete=models.CASCADE,
        related_name="participant_records",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="live_participant_records",
    )
    is_muted = models.BooleanField(default=False)
    hand_raised = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "user")

    def __str__(self):
        return f"{self.user} in {self.session}"


# Import AI/live-class models so Django registers them.
from backend.live_class.models import AISummary, AIQuestion, AIInsight, TranscriptSegment  # noqa: E402
