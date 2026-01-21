from django.contrib import admin

from .models import (
    Choice,
    ExamAnswer,
    ExamAttempt,
    ExamOption,
    ExamQuestion,
    Formula,
    Grade,
    Lesson,
    LessonBookmark,
    LessonNote,
    Progress,
    Question,
    Quiz,
    QuizResult,
    StudentProgress,
    Subject,
    Subtopic,
    Topic,
)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "grade", "created_at")
    list_filter = ("subject", "grade", "subject_ref", "grade_ref")
    search_fields = ("title", "content", "subject", "notes_text")
    ordering = ("-created_at",)


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "mark", "completed", "completed_at")
    list_filter = ("completed",)
    search_fields = ("student__username", "lesson__title")


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson")
    search_fields = ("title", "lesson__title")


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("quiz", "text")
    search_fields = ("quiz__title", "text")


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")
    search_fields = ("question__text", "text")


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "completed_at")
    search_fields = ("student__username", "quiz__title")
    ordering = ("-completed_at",)


@admin.register(Formula)
class FormulaAdmin(admin.ModelAdmin):
    list_display = ("grade", "subject", "topic", "created_at")
    list_filter = ("grade", "subject")
    search_fields = ("topic", "formula_text", "explanation")
    ordering = ("grade", "subject", "topic")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = ("number", "label")
    ordering = ("number",)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "subject", "grade")
    list_filter = ("subject", "grade")
    search_fields = ("name",)


@admin.register(Subtopic)
class SubtopicAdmin(admin.ModelAdmin):
    list_display = ("name", "topic")
    list_filter = ("topic",)
    search_fields = ("name",)


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "completed", "completed_at", "last_opened_at")
    list_filter = ("completed",)
    search_fields = ("student__username", "lesson__title")


@admin.register(LessonBookmark)
class LessonBookmarkAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "created_at")
    search_fields = ("student__username", "lesson__title")


@admin.register(LessonNote)
class LessonNoteAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "created_at")
    search_fields = ("student__username", "lesson__title", "content")


@admin.register(ExamQuestion)
class ExamQuestionAdmin(admin.ModelAdmin):
    list_display = ("exam", "question_type", "points")
    list_filter = ("question_type",)


@admin.register(ExamOption)
class ExamOptionAdmin(admin.ModelAdmin):
    list_display = ("question", "text", "is_correct")


@admin.register(ExamAttempt)
class ExamAttemptAdmin(admin.ModelAdmin):
    list_display = ("exam", "student", "score", "started_at", "completed_at")
    list_filter = ("exam",)


@admin.register(ExamAnswer)
class ExamAnswerAdmin(admin.ModelAdmin):
    list_display = ("attempt", "question", "is_correct", "score_awarded")