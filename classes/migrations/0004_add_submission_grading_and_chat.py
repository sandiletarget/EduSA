from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("classes", "0003_add_assessment_grade_subject"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessmentsubmission",
            name="mark",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assessmentsubmission",
            name="feedback",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="assessmentsubmission",
            name="graded_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name="ChatMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="chat_messages", to="classes.class")),
                ("sender", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="classroom_messages", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("created_at",),
            },
        ),
    ]
