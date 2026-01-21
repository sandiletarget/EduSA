from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_add_exam_model"),
    ]

    operations = [
        migrations.CreateModel(
            name="Formula",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("grade", models.PositiveSmallIntegerField()),
                ("subject", models.CharField(choices=[("mathematics", "Mathematics"), ("physical_sciences", "Physical Sciences"), ("accounting", "Accounting"), ("geography", "Geography"), ("life_sciences", "Life Sciences")], max_length=50)),
                ("topic", models.CharField(max_length=120)),
                ("formula_text", models.TextField()),
                ("explanation", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("grade", "subject", "topic"),
            },
        ),
    ]
