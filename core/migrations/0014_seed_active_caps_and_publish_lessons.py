from django.db import migrations
from django.utils import timezone


def seed_caps_and_publish(apps, schema_editor):
    CAPSVersion = apps.get_model("core", "CAPSVersion")
    Lesson = apps.get_model("core", "Lesson")

    year = timezone.now().year
    caps, _ = CAPSVersion.objects.get_or_create(
        year=year,
        defaults={"description": f"CAPS {year}", "is_active": True},
    )

    if not CAPSVersion.objects.filter(is_active=True).exists():
        caps.is_active = True
        caps.save(update_fields=["is_active"])

    Lesson.objects.filter(caps_version__isnull=True).update(caps_version=caps)
    Lesson.objects.filter(is_published=False).update(is_published=True)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_lms_course_and_tracking"),
    ]

    operations = [
        migrations.RunPython(seed_caps_and_publish, noop),
    ]
