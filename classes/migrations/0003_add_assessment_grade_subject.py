from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("classes", "0002_add_assessments"),
        ("core", "0009_seed_grades_subjects"),
    ]

    operations = [
        migrations.AddField(
            model_name="assessment",
            name="grade_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assessments", to="core.grade"),
        ),
        migrations.AddField(
            model_name="assessment",
            name="subject_ref",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="assessments", to="core.subject"),
        ),
    ]
