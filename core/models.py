import uuid
from django.utils.text import slugify

from django.conf import settings
from django.db import models


class Grade(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    label = models.CharField(max_length=20, default="")

    class Meta:
        ordering = ("number",)

    def __str__(self):
        return self.label or f"Grade {self.number}"


class Subject(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    grades = models.ManyToManyField(Grade, related_name="subjects", blank=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return self.name


class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="topics")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="topics")
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ("grade", "subject", "name")
        unique_together = ("subject", "grade", "name")

    def __str__(self):
        return f"{self.name} ({self.subject.name})"


class Subtopic(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="subtopics")
    name = models.CharField(max_length=150)

    class Meta:
        ordering = ("topic", "name")
        unique_together = ("topic", "name")

    def __str__(self):
        return self.name


class Lesson(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    content = models.TextField()
    grade = models.CharField(max_length=20, blank=True, default="")
    subject = models.CharField(max_length=50, blank=True, default="")
    grade_ref = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons")
    subject_ref = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons")
    topic_ref = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons")
    subtopic_ref = models.ForeignKey("Subtopic", on_delete=models.SET_NULL, null=True, blank=True, related_name="lessons")
    notes_text = models.TextField(blank=True, default="")
    notes_file = models.FileField(upload_to="lesson_notes/", blank=True, null=True)
    video_url = models.URLField(blank=True, default="")
    formula_sheet = models.FileField(upload_to="formula_sheets/", blank=True, null=True)
    cover_image = models.FileField(upload_to="lesson_images/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "lesson"
            candidate = base
            idx = 1
            while Lesson.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                idx += 1
                candidate = f"{base}-{idx}"
            self.slug = candidate
        super().save(*args, **kwargs)

    @property
    def description(self):
        return self.content

    @description.setter
    def description(self, value):
        self.content = value


class Progress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress"
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="progress_records"
    )
    mark = models.PositiveIntegerField(help_text="Percentage mark (0–100)", default=0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")

    def __str__(self):
        return f"{self.student} - {self.lesson} ({self.mark}%)"


LessonProgress = Progress


class StudentProgress(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_progress_records",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="student_progress",
    )
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_opened_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("student", "lesson")

    def __str__(self):
        return f"{self.student} - {self.lesson}"


class Quiz(models.Model):
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name="quiz"
    )
    title = models.CharField(max_length=200)

    def __str__(self):
        return self.title


class Question(models.Model):
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions"
    )
    text = models.CharField(max_length=500)

    def __str__(self):
        return self.text


class Choice(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="choices"
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class QuizResult(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_results"
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="results"
    )
    score = models.IntegerField()
    completed_at = models.DateTimeField(auto_now_add=True)
    certificate_code = models.CharField(max_length=36, blank=True, null=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.certificate_code and self.score >= 50:
            self.certificate_code = str(uuid.uuid4())
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.quiz} - {self.score}%"


class Exam(models.Model):
    classroom = models.ForeignKey(
        "classes.Class",
        on_delete=models.CASCADE,
        related_name="exams",
    )
    grade_ref = models.ForeignKey(Grade, on_delete=models.SET_NULL, null=True, blank=True, related_name="exams")
    subject_ref = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True, related_name="exams")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    due_date = models.DateField(null=True, blank=True)
    duration_minutes = models.PositiveIntegerField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exams_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class LessonBookmark(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_bookmarks",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="bookmarks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "lesson")

    def __str__(self):
        return f"{self.student} bookmarked {self.lesson}"


class LessonNote(models.Model):
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="lesson_notes",
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"Note for {self.lesson}"


class ExamQuestion(models.Model):
    TYPE_MULTIPLE_CHOICE = "mcq"
    TYPE_TRUE_FALSE = "true_false"
    TYPE_SHORT = "short"
    TYPE_NUMERIC = "numeric"
    TYPE_FORMULA = "formula"

    QUESTION_TYPES = [
        (TYPE_MULTIPLE_CHOICE, "Multiple choice"),
        (TYPE_TRUE_FALSE, "True/False"),
        (TYPE_SHORT, "Short answer"),
        (TYPE_NUMERIC, "Numerical"),
        (TYPE_FORMULA, "Formula"),
    ]

    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="questions")
    prompt = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
    points = models.PositiveIntegerField(default=1)
    correct_answer = models.TextField(blank=True)

    def __str__(self):
        return self.prompt[:60]


class ExamOption(models.Model):
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name="options")
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name="attempts")
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="exam_attempts")
    score = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)

    def __str__(self):
        return f"{self.student} - {self.exam}"


class ExamAnswer(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name="answers")
    question = models.ForeignKey(ExamQuestion, on_delete=models.CASCADE, related_name="answers")
    selected_option = models.ForeignKey(ExamOption, on_delete=models.SET_NULL, null=True, blank=True)
    answer_text = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    score_awarded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Answer for {self.question_id}"


class Formula(models.Model):
    SUBJECT_CHOICES = [
        ("mathematics", "Mathematics"),
        ("physical_sciences", "Physical Sciences"),
        ("accounting", "Accounting"),
        ("geography", "Geography"),
        ("life_sciences", "Life Sciences"),
    ]

    grade = models.PositiveSmallIntegerField()
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    topic = models.CharField(max_length=120)
    formula_text = models.TextField()
    explanation = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("grade", "subject", "topic")

    def __str__(self):
        return f"Grade {self.grade} {self.get_subject_display()} - {self.topic}"
