from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string

from core.models import Grade, Subject

from core.utils import resolve_user_role


class Class(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="classes",
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    passcode = models.CharField(max_length=8, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name_plural = "classes"

    def __str__(self):
        return self.name

    @staticmethod
    def _generate_passcode(length=8):
        allowed = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
        while True:
            code = get_random_string(length=length, allowed_chars=allowed)
            if not Class.objects.filter(passcode=code).exists():
                return code

    def clean(self):
        super().clean()
        if self.teacher_id and resolve_user_role(self.teacher) != "teacher":
            raise ValidationError({
                "teacher": "Only teacher accounts may own classes."
            })

    def save(self, *args, **kwargs):
        if not self.passcode:
            self.passcode = self._generate_passcode()
        self.full_clean()
        super().save(*args, **kwargs)


class ClassMembership(models.Model):
    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="memberships"
    )
    learner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="class_memberships"
    )
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("classroom", "learner")
        ordering = ("-joined_at",)

    def __str__(self):
        return f"{self.learner} @ {self.classroom.name}"

    def clean(self):
        super().clean()
        if self.learner and self.learner.is_staff:
            raise ValidationError({
                "learner": "Teachers should not enroll as learners."
            })


class LiveSession(models.Model):
    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="live_sessions"
    )
    is_active = models.BooleanField(default=False)
    started_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Live session for {self.classroom.name}"


class Assessment(models.Model):
    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="assessments",
    )
    grade_ref = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")
    subject_ref = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="assessments")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessments_created",
    )
    title = models.CharField(max_length=200)
    instructions = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    allowed_file_types = models.CharField(
        max_length=200,
        default="pdf,docx,jpg,jpeg,png",
        help_text="Comma-separated list of allowed extensions",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title

    def allowed_extensions(self):
        return [ext.strip().lower() for ext in self.allowed_file_types.split(",") if ext.strip()]


class AssessmentSubmission(models.Model):
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name="submissions",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessment_submissions",
    )
    submission_file = models.FileField(upload_to="assessment_submissions/")
    submitted_at = models.DateTimeField(auto_now_add=True)
    mark = models.PositiveSmallIntegerField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-submitted_at",)
        unique_together = ("assessment", "student")

    def __str__(self):
        return f"{self.student} - {self.assessment}"

    @property
    def is_late(self):
        due_date = self.assessment.due_date
        if not due_date or not self.submitted_at:
            return False
        return self.submitted_at.date() > due_date


class ChatMessage(models.Model):
    classroom = models.ForeignKey(
        Class,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="classroom_messages",
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("created_at",)

    def __str__(self):
        return f"{self.sender} - {self.classroom.name}"
