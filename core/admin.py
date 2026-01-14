from django.contrib import admin

from .models import Choice, Lesson, Progress, Question, Quiz, QuizResult


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "subject", "grade", "created_at")
    list_filter = ("subject", "grade")
    search_fields = ("title", "content", "subject")
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