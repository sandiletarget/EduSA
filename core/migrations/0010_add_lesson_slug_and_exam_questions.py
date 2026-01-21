from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def backfill_lesson_slugs(apps, schema_editor):
    Lesson = apps.get_model("core", "Lesson")
    for lesson in Lesson.objects.all():
        if lesson.slug:
            continue
        base = "lesson"
        title = getattr(lesson, "title", "") or "lesson"
        slug = "-".join(title.lower().split())
        base = slug or "lesson"
        candidate = base
        idx = 1
        while Lesson.objects.filter(slug=candidate).exclude(pk=lesson.pk).exists():
            idx += 1
            candidate = f"{base}-{idx}"
        lesson.slug = candidate
        lesson.save(update_fields=["slug"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_seed_grades_subjects"),
    ]

    operations = [
        migrations.CreateModel(
            name="Subtopic",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=150)),
                ("topic", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="subtopics", to="core.topic")),
            ],
            options={
                "ordering": ("topic", "name"),
                "unique_together": {("topic", "name")},
            },
        ),
        migrations.AddField(
            model_name="lesson",
            name="slug",
            field=models.SlugField(blank=True, max_length=220, null=True, unique=True),
        ),
        migrations.AddField(
            model_name="lesson",
            name="subtopic_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lessons", to="core.subtopic"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="cover_image",
            field=models.FileField(blank=True, null=True, upload_to="lesson_images/"),
        ),
        migrations.AddField(
            model_name="exam",
            name="grade_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="exams", to="core.grade"),
        ),
        migrations.AddField(
            model_name="exam",
            name="subject_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="exams", to="core.subject"),
        ),
        migrations.AddField(
            model_name="exam",
            name="duration_minutes",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="exam",
            name="is_published",
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name="LessonBookmark",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookmarks", to="core.lesson")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lesson_bookmarks", to=settings.AUTH_USER_MODEL)),
            ],
            options={"unique_together": {("student", "lesson")}},
        ),
        migrations.CreateModel(
            name="LessonNote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notes", to="core.lesson")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lesson_notes", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.CreateModel(
            name="ExamQuestion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("prompt", models.TextField()),
                ("question_type", models.CharField(choices=[("mcq", "Multiple choice"), ("true_false", "True/False"), ("short", "Short answer"), ("numeric", "Numerical"), ("formula", "Formula")], max_length=30)),
                ("points", models.PositiveIntegerField(default=1)),
                ("correct_answer", models.TextField(blank=True)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="questions", to="core.exam")),
            ],
        ),
        migrations.CreateModel(
            name="ExamOption",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("text", models.CharField(max_length=300)),
                ("is_correct", models.BooleanField(default=False)),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="options", to="core.examquestion")),
            ],
        ),
        migrations.CreateModel(
            name="ExamAttempt",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveIntegerField(default=0)),
                ("started_at", models.DateTimeField(auto_now_add=True)),
                ("completed_at", models.DateTimeField(blank=True, null=True)),
                ("exam", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="attempts", to="core.exam")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="exam_attempts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-started_at",)},
        ),
        migrations.CreateModel(
            name="ExamAnswer",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("answer_text", models.TextField(blank=True)),
                ("is_correct", models.BooleanField(default=False)),
                ("score_awarded", models.PositiveIntegerField(default=0)),
                ("attempt", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="core.examattempt")),
                ("question", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="answers", to="core.examquestion")),
                ("selected_option", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="core.examoption")),
            ],
        ),
        migrations.RunPython(backfill_lesson_slugs),
    ]
