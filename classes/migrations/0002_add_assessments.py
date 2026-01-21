from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("classes", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Assessment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("instructions", models.TextField(blank=True)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("allowed_file_types", models.CharField(default="pdf,docx,jpg,jpeg,png", help_text="Comma-separated list of allowed extensions", max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("classroom", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assessments", to="classes.class")),
                ("teacher", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assessments_created", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="AssessmentSubmission",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("submission_file", models.FileField(upload_to="assessment_submissions/")),
                ("submitted_at", models.DateTimeField(auto_now_add=True)),
                ("assessment", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="submissions", to="classes.assessment")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="assessment_submissions", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-submitted_at",),
                "unique_together": {("assessment", "student")},
            },
        ),
    ]
