from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_caps_version_and_curriculum_fields"),
    ]

    operations = [
        migrations.CreateModel(
            name="UserRole",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("role", models.CharField(choices=[("admin", "Admin"), ("curriculum_admin", "Curriculum Admin"), ("teacher", "Teacher"), ("student", "Student"), ("reviewer", "Read-only Reviewer")], default="student", max_length=40)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="role_profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Course",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(blank=True, default="", max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("caps_version", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="courses", to="core.capsversion")),
                ("grade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="courses", to="core.grade")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="courses", to="core.subject")),
            ],
            options={
                "ordering": ("grade__number", "subject__name"),
                "unique_together": {("caps_version", "grade", "subject")},
            },
        ),
        migrations.CreateModel(
            name="CourseEnrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_teacher", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                ("enrolled_at", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="core.course")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="course_enrollments", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("course", "user")},
            },
        ),
        migrations.CreateModel(
            name="Resource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("resource_type", models.CharField(choices=[("pdf", "PDF"), ("video", "Video"), ("link", "External Link"), ("file", "File")], default="file", max_length=20)),
                ("file", models.FileField(blank=True, null=True, upload_to="resources/")),
                ("url", models.URLField(blank=True, default="")),
                ("is_published", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("caps_version", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resources", to="core.capsversion")),
                ("grade", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resources", to="core.grade")),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resources", to="core.subject")),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="LessonResource",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("lesson", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="resources", to="core.lesson")),
                ("resource", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="lesson_links", to="core.resource")),
            ],
            options={
                "unique_together": {("lesson", "resource")},
            },
        ),
        migrations.CreateModel(
            name="CourseAnnouncement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("is_published", models.BooleanField(default=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="announcements", to="core.course")),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("message", models.TextField()),
                ("link", models.CharField(blank=True, default="", max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("read_at", models.DateTimeField(blank=True, null=True)),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="CourseProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("percent_complete", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="progress_records", to="core.course")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="course_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("user", "course")},
            },
        ),
        migrations.CreateModel(
            name="CourseTermProgress",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("term", models.PositiveSmallIntegerField(choices=[(1, "Term 1"), (2, "Term 2"), (3, "Term 3"), (4, "Term 4")])) ,
                ("completed", models.BooleanField(default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="term_progress", to="core.course")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="term_progress", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "unique_together": {("user", "course", "term")},
            },
        ),
        migrations.CreateModel(
            name="ActivityLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(choices=[("lesson_view", "Lesson View"), ("lesson_complete", "Lesson Complete"), ("submission", "Assessment Submission"), ("grade", "Assessment Graded")], max_length=30)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activity_logs", to="core.course")),
                ("lesson", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="activity_logs", to="core.lesson")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="activity_logs", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("action", models.CharField(max_length=100)),
                ("target", models.CharField(blank=True, default="", max_length=200)),
                ("metadata", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("actor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
    ]
