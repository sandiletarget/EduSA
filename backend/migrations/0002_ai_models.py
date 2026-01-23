from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("backend", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="liveclasssession",
            name="ai_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="liveclasssession",
            name="ai_mode",
            field=models.CharField(default="passive", max_length=20),
        ),
        migrations.AddField(
            model_name="liveclasssession",
            name="chat_enabled",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="liveclasssession",
            name="allow_student_drawing",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="TranscriptSegment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.TextField()),
                ("start_time", models.FloatField(default=0.0)),
                ("end_time", models.FloatField(default=0.0)),
                ("is_flagged", models.BooleanField(default=False)),
                ("flag_reason", models.CharField(blank=True, max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("live_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="transcript_segments", to="backend.liveclasssession")),
                ("speaker", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="transcript_segments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("created_at",),
            },
        ),
        migrations.CreateModel(
            name="AISummary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("is_approved", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("live_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_summaries", to="backend.liveclasssession")),
            ],
        ),
        migrations.CreateModel(
            name="AIQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("question", models.TextField()),
                ("answer", models.TextField(blank=True)),
                ("status", models.CharField(choices=[("suggested", "Suggested"), ("answered", "Answered"), ("flagged", "Flagged")], default="suggested", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("asked_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="ai_questions", to=settings.AUTH_USER_MODEL)),
                ("live_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_questions", to="backend.liveclasssession")),
            ],
        ),
        migrations.CreateModel(
            name="AIInsight",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("insight_type", models.CharField(choices=[("participation", "Participation"), ("attendance", "Attendance"), ("moderation", "Moderation")], max_length=20)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("live_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="ai_insights", to="backend.liveclasssession")),
            ],
        ),
    ]
