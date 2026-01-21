from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_seed_formula_examples"),
    ]

    operations = [
        migrations.CreateModel(
            name="Grade",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.PositiveSmallIntegerField(unique=True)),
                ("label", models.CharField(default="", max_length=20)),
            ],
            options={"ordering": ("number",)},
        ),
        migrations.CreateModel(
            name="Subject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=120, unique=True)),
            ],
            options={"ordering": ("name",)},
        ),
        migrations.CreateModel(
            name="Topic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("grade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="topics", to="core.grade")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="topics", to="core.subject")),
            ],
            options={
                "ordering": ("grade", "subject", "name"),
                "unique_together": {("subject", "grade", "name")},
            },
        ),
        migrations.AddField(
            model_name="subject",
            name="grades",
            field=models.ManyToManyField(blank=True, related_name="subjects", to="core.grade"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="formula_sheet",
            field=models.FileField(blank=True, null=True, upload_to="formula_sheets/"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="grade_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lessons", to="core.grade"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="notes_file",
            field=models.FileField(blank=True, null=True, upload_to="lesson_notes/"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="notes_text",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="lesson",
            name="subject_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lessons", to="core.subject"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="topic_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lessons", to="core.topic"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="video_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.CreateModel(
            name="StudentProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("completed", models.BooleanField(default=False)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("last_opened_at", models.DateTimeField(blank=True, null=True)),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_progress", to="core.lesson")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lesson_progress_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("student", "lesson")}},
        ),
    ]
