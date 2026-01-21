from django.db import migrations
from django.utils import timezone


def seed_exam(apps, schema_editor):
    Exam = apps.get_model("core", "Exam")
    ExamQuestion = apps.get_model("core", "ExamQuestion")
    ExamOption = apps.get_model("core", "ExamOption")
    Grade = apps.get_model("core", "Grade")
    Subject = apps.get_model("core", "Subject")
    User = apps.get_model("auth", "User")
    Classroom = apps.get_model("classes", "Class")

    teacher = User.objects.filter(is_staff=True).first()
    classroom = Classroom.objects.first()
    if not teacher or not classroom:
        return

    grade = Grade.objects.filter(number=10).first()
    subject = Subject.objects.filter(slug="mathematics").first()

    exam, _ = Exam.objects.get_or_create(
        title="Sample Mathematics Exam",
        defaults={
            "classroom_id": classroom.id,
            "created_by": teacher,
            "description": "Sample mixed question types.",
            "is_published": True,
            "duration_minutes": 45,
            "grade_ref": grade,
            "subject_ref": subject,
            "created_at": timezone.now(),
        },
    )

    if exam.questions.exists():
        return

    q1 = ExamQuestion.objects.create(exam=exam, prompt="2 + 2 = ?", question_type="mcq", points=1, correct_answer="4")
    ExamOption.objects.create(question=q1, text="3", is_correct=False)
    ExamOption.objects.create(question=q1, text="4", is_correct=True)
    ExamOption.objects.create(question=q1, text="5", is_correct=False)

    q2 = ExamQuestion.objects.create(exam=exam, prompt="The square root of 81 is 9.", question_type="true_false", points=1, correct_answer="true")
    ExamOption.objects.create(question=q2, text="True", is_correct=True)
    ExamOption.objects.create(question=q2, text="False", is_correct=False)

    ExamQuestion.objects.create(exam=exam, prompt="Simplify: 5x + 2x", question_type="short", points=2, correct_answer="7x")
    ExamQuestion.objects.create(exam=exam, prompt="Calculate: 12 ÷ 4", question_type="numeric", points=1, correct_answer="3")
    ExamQuestion.objects.create(exam=exam, prompt="State the quadratic formula.", question_type="formula", points=3, correct_answer="x = (-b ± √(b² - 4ac)) / 2a")


def unseed_exam(apps, schema_editor):
    Exam = apps.get_model("core", "Exam")
    Exam.objects.filter(title="Sample Mathematics Exam").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_add_lesson_slug_and_exam_questions"),
    ]

    operations = [
        migrations.RunPython(seed_exam, unseed_exam),
    ]
