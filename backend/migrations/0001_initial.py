from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("classes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="LiveClassSession",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("scheduled", "Scheduled"), ("live", "Live"), ("ended", "Ended")], default="scheduled", max_length=20)),
                ("locked", models.BooleanField(default=False)),
                ("started_at", models.DateTimeField(blank=True, null=True)),
                ("ended_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="live_class_sessions", to="classes.class")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="hosted_live_classes", to=settings.AUTH_USER_MODEL)),
                ("participants", models.ManyToManyField(blank=True, related_name="live_class_participations", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="LiveParticipant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_muted", models.BooleanField(default=False)),
                ("hand_raised", models.BooleanField(default=False)),
                ("joined_at", models.DateTimeField(auto_now_add=True)),
                ("session", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="participant_records", to="backend.liveclasssession")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="live_participant_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("session", "user")},
            },
        ),
    ]
