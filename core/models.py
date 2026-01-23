import uuid

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils.text import slugify


class CAPSVersion(models.Model):
    year = models.PositiveSmallIntegerField(unique=True)
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-year",)
        constraints = [
            models.UniqueConstraint(
                fields=["is_active"],
                condition=Q(is_active=True),
                name="single_active_caps_version",
            )
        ]

    def __str__(self):
        return f"CAPS {self.year}"

    def save(self, *args, **kwargs):
        if self.is_active:
            CAPSVersion.objects.exclude(pk=self.pk).filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()


class UserRole(models.Model):
    ROLE_ADMIN = "admin"
    ROLE_CURRICULUM_ADMIN = "curriculum_admin"
    ROLE_TEACHER = "teacher"
    ROLE_STUDENT = "student"
    ROLE_REVIEWER = "reviewer"

    ROLE_CHOICES = [
        (ROLE_ADMIN, "Admin"),
        (ROLE_CURRICULUM_ADMIN, "Curriculum Admin"),
        (ROLE_TEACHER, "Teacher"),
        (ROLE_STUDENT, "Student"),
        (ROLE_REVIEWER, "Read-only Reviewer"),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="role_profile")
    role = models.CharField(max_length=40, choices=ROLE_CHOICES, default=ROLE_STUDENT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} ({self.role})"


class Grade(models.Model):
    PHASE_INTERMEDIATE = "intermediate"
    PHASE_SENIOR = "senior"
    PHASE_FET = "fet"
    PHASE_CHOICES = [
        (PHASE_INTERMEDIATE, "Intermediate"),
        (PHASE_SENIOR, "Senior"),
        (PHASE_FET, "FET"),
    ]

    number = models.PositiveSmallIntegerField(unique=True)
    label = models.CharField(max_length=20, default="")
    phase = models.CharField(max_length=20, choices=PHASE_CHOICES, default=PHASE_INTERMEDIATE)

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


class Course(models.Model):
    caps_version = models.ForeignKey(CAPSVersion, on_delete=models.CASCADE, related_name="courses")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="courses")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="courses")
    title = models.CharField(max_length=200, blank=True, default="")
    description = models.TextField(blank=True, default="")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("caps_version", "grade", "subject")
        ordering = ("grade__number", "subject__name")

    def __str__(self):
        return self.title or f"{self.subject.name} Grade {self.grade.number} ({self.caps_version.year})"


class CourseEnrollment(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_enrollments")
    is_teacher = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("course", "user")

    def __str__(self):
        return f"{self.user} -> {self.course}"


class Lesson(models.Model):
    caps_version = models.ForeignKey(
        CAPSVersion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lessons",
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True, null=True)
    term = models.PositiveSmallIntegerField(choices=[(1, "Term 1"), (2, "Term 2"), (3, "Term 3"), (4, "Term 4")], default=1)
    topic = models.CharField(max_length=200, blank=True, default="")
    content = models.TextField()
    key_concepts = models.TextField(blank=True, default="")
    examples = models.TextField(blank=True, default="")
    summary = models.TextField(blank=True, default="")
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
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.caps_version:
            active_caps = CAPSVersion.get_active()
            if active_caps:
                self.caps_version = active_caps
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

    @classmethod
    def published_for_active_caps(cls):
        return cls.objects.filter(is_published=True, caps_version__is_active=True)


class Resource(models.Model):
    TYPE_PDF = "pdf"
    TYPE_VIDEO = "video"
    TYPE_LINK = "link"
    TYPE_FILE = "file"

    TYPE_CHOICES = [
        (TYPE_PDF, "PDF"),
        (TYPE_VIDEO, "Video"),
        (TYPE_LINK, "External Link"),
        (TYPE_FILE, "File"),
    ]

    caps_version = models.ForeignKey(CAPSVersion, on_delete=models.CASCADE, related_name="resources")
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name="resources")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="resources")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    resource_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_FILE)
    file = models.FileField(upload_to="resources/", blank=True, null=True)
    url = models.URLField(blank=True, default="")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class LessonResource(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name="resources")
    resource = models.ForeignKey("Resource", on_delete=models.CASCADE, related_name="lesson_links")

    class Meta:
        unique_together = ("lesson", "resource")

    def __str__(self):
        return f"{self.lesson} -> {self.resource}"


class CourseAnnouncement(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="announcements")
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=200)
    message = models.TextField()
    link = models.CharField(max_length=200, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.title}"


class CourseProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="course_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="progress_records")
    percent_complete = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user} - {self.course} ({self.percent_complete}%)"


class CourseTermProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="term_progress")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="term_progress")
    term = models.PositiveSmallIntegerField(choices=[(1, "Term 1"), (2, "Term 2"), (3, "Term 3"), (4, "Term 4")])
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "course", "term")

    def __str__(self):
        return f"{self.user} - {self.course} (Term {self.term})"


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ("lesson_view", "Lesson View"),
        ("lesson_complete", "Lesson Complete"),
        ("submission", "Assessment Submission"),
        ("grade", "Assessment Graded"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="activity_logs")
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    lesson = models.ForeignKey(Lesson, on_delete=models.SET_NULL, null=True, blank=True, related_name="activity_logs")
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.user} - {self.action}"


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    target = models.CharField(max_length=200, blank=True, default="")
    metadata = models.JSONField(blank=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.action} - {self.target}"


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


class ExamQuestion(models.Model):
    QUESTION_TYPE_CHOICES = [
        ("mcq", "Multiple choice"),
        ("true_false", "True/False"),
        ("short", "Short answer"),
        ("numeric", "Numerical"),
        ("formula", "Formula"),
    ]

    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="questions",
    )
    prompt = models.TextField()
    question_type = models.CharField(max_length=30, choices=QUESTION_TYPE_CHOICES)
    points = models.PositiveIntegerField(default=1)
    correct_answer = models.TextField(blank=True)

    def __str__(self):
        return f"{self.exam.title} - {self.question_type}"


class ExamOption(models.Model):
    question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.CASCADE,
        related_name="options",
    )
    text = models.CharField(max_length=300)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.text


class ExamAttempt(models.Model):
    exam = models.ForeignKey(
        Exam,
        on_delete=models.CASCADE,
        related_name="attempts",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="exam_attempts",
    )
    score = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-started_at",)

    def __str__(self):
        return f"{self.student} - {self.exam.title}"


class ExamAnswer(models.Model):
    attempt = models.ForeignKey(
        ExamAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    question = models.ForeignKey(
        ExamQuestion,
        on_delete=models.CASCADE,
        related_name="answers",
    )
    selected_option = models.ForeignKey(
        ExamOption,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    answer_text = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    score_awarded = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.attempt} - {self.question}"


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
        return f"{self.subject} Grade {self.grade}: {self.topic}"


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
        return f"{self.student} - {self.lesson}"


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
        return f"{self.student} - {self.lesson}"
