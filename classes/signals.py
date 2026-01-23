import hashlib

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from classes.models import AssessmentSubmission
from core.models import Notification


@receiver(pre_save, sender=AssessmentSubmission)
def set_submission_hash(sender, instance, **kwargs):
    if instance.submission_file and not instance.file_hash:
        try:
            hasher = hashlib.sha256()
            for chunk in instance.submission_file.chunks():
                hasher.update(chunk)
            instance.file_hash = hasher.hexdigest()
        except Exception:
            instance.file_hash = instance.file_hash or ""

    if not instance.pk:
        previous = AssessmentSubmission.objects.filter(assessment=instance.assessment, student=instance.student).count()
        instance.attempt_number = previous + 1


@receiver(post_save, sender=AssessmentSubmission)
def notify_submission_graded(sender, instance, created, **kwargs):
    if created:
        return
    if not instance.graded_at:
        return

    Notification.objects.create(
        user=instance.student,
        title=f"Assessment graded: {instance.assessment.title}",
        message=f"Your submission has been graded. Mark: {instance.mark or 'N/A'}.",
        link=f"/classes/assessments/{instance.assessment.id}/submit/",
    )

    if instance.student.email:
        send_mail(
            subject=f"Assessment graded: {instance.assessment.title}",
            message=f"Your submission has been graded. Mark: {instance.mark or 'N/A'}.",
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
            recipient_list=[instance.student.email],
            fail_silently=True,
        )
