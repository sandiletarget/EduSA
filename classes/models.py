from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.crypto import get_random_string

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
