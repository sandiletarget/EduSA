from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("classes", "0004_add_submission_grading_and_chat"),
    ]

    operations = [
        migrations.CreateModel(
            name="Rubric",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="RubricCriterion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True, default="")),
                ("max_score", models.PositiveSmallIntegerField(default=5)),
                ("order", models.PositiveSmallIntegerField(default=1)),
                ("rubric", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="criteria", to="classes.rubric")),
            ],
            options={
                "ordering": ("order",),
            },
        ),
        migrations.CreateModel(
            name="RubricScore",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("score", models.PositiveSmallIntegerField(default=0)),
                ("comment", models.TextField(blank=True, default="")),
                ("graded_at", models.DateTimeField(auto_now=True)),
                ("criterion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="scores", to="classes.rubriccriterion")),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rubric_scores", to="classes.assessmentsubmission")),
            ],
            options={
                "unique_together": {("submission", "criterion")},
            },
        ),
        migrations.CreateModel(
            name="SubmissionComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("author", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="auth.user")),
                ("submission", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="comments", to="classes.assessmentsubmission")),
            ],
            options={
                "ordering": ("-created_at",),
            },
        ),
        migrations.AddField(
            model_name="assessment",
            name="allow_resubmission",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="assessment",
            name="attempt_limit",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="assessment",
            name="rubric",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assessments", to="classes.rubric"),
        ),
        migrations.AddField(
            model_name="assessmentsubmission",
            name="attempt_number",
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name="assessmentsubmission",
            name="file_hash",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
    ]
