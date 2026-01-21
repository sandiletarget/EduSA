from django.db import migrations


def seed_grades_subjects(apps, schema_editor):
    Grade = apps.get_model("core", "Grade")
    Subject = apps.get_model("core", "Subject")

    grade_numbers = list(range(4, 13))
    grades = {}
    for number in grade_numbers:
        grade, _ = Grade.objects.get_or_create(number=number, defaults={"label": f"Grade {number}"})
        grades[number] = grade

    subjects = [
        ("Mathematics", "mathematics"),
        ("Physical Sciences", "physical-sciences"),
        ("Life Sciences", "life-sciences"),
        ("Natural Sciences", "natural-sciences"),
        ("History", "history"),
        ("Geography", "geography"),
        ("Economics", "economics"),
        ("EMS", "ems"),
        ("Technology", "technology"),
    ]

    for name, slug in subjects:
        subject, _ = Subject.objects.get_or_create(name=name, slug=slug)
        subject.grades.set(list(grades.values()))


def unseed_grades_subjects(apps, schema_editor):
    Subject = apps.get_model("core", "Subject")
    Grade = apps.get_model("core", "Grade")
    Subject.objects.all().delete()
    Grade.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0008_add_grade_subject_topic_and_lesson_fields"),
    ]

    operations = [
        migrations.RunPython(seed_grades_subjects, unseed_grades_subjects),
    ]
