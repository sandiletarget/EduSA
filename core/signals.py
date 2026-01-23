from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

from core.models import CourseAnnouncement, CourseEnrollment, Notification


@receiver(post_save, sender=CourseAnnouncement)
def notify_course_announcement(sender, instance, created, **kwargs):
    if not created or not instance.is_published:
        return

    enrollments = CourseEnrollment.objects.filter(course=instance.course, is_active=True)
    for enrollment in enrollments:
        Notification.objects.create(
            user=enrollment.user,
            title=f"Announcement: {instance.title}",
            message=instance.message,
            link=f"/courses/{instance.course.id}/",
        )
        if enrollment.user.email:
            send_mail(
                subject=f"Course announcement: {instance.title}",
                message=instance.message,
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
                recipient_list=[enrollment.user.email],
                fail_silently=True,
            )
