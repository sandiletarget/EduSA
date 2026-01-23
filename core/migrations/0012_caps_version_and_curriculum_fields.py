from django.db import migrations, models
import django.db.models.deletion
from django.db.models import Q


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_seed_example_exam"),
    ]

    operations = [
        migrations.CreateModel(
            name="CAPSVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("year", models.PositiveSmallIntegerField(unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("is_active", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-year",),
            },
        ),
        migrations.AddConstraint(
            model_name="capsversion",
            constraint=models.UniqueConstraint(condition=Q(("is_active", True)), fields=("is_active",), name="single_active_caps_version"),
        ),
        migrations.AddField(
            model_name="grade",
            name="phase",
            field=models.CharField(choices=[("intermediate", "Intermediate"), ("senior", "Senior"), ("fet", "FET")], default="intermediate", max_length=20),
        ),
        migrations.AddField(
            model_name="lesson",
            name="caps_version",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="lessons", to="core.capsversion"),
        ),
        migrations.AddField(
            model_name="lesson",
            name="examples",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="lesson",
            name="is_published",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="lesson",
            name="key_concepts",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="lesson",
            name="summary",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="lesson",
            name="term",
            field=models.PositiveSmallIntegerField(choices=[(1, "Term 1"), (2, "Term 2"), (3, "Term 3"), (4, "Term 4")], default=1),
        ),
        migrations.AddField(
            model_name="lesson",
            name="topic",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="lesson",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
    ]
