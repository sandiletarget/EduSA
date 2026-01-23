from django.contrib import admin
from django import forms
from ckeditor.widgets import CKEditorWidget

from .models import (
    ActivityLog,
    AuditLog,
    CAPSVersion,
    Choice,
    Course,
    CourseAnnouncement,
    CourseEnrollment,
    CourseProgress,
    CourseTermProgress,
    ExamAnswer,
    ExamAttempt,
    ExamOption,
    ExamQuestion,
    Formula,
    Grade,
    Lesson,
    LessonBookmark,
    LessonNote,
    LessonResource,
    Notification,
    Progress,
    Question,
    Quiz,
    QuizResult,
    Resource,
    StudentProgress,
    Subject,
    Subtopic,
    Topic,
    UserRole,
)


class LessonAdminForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())

    class Meta:
        model = Lesson
        fields = "__all__"

@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    form = LessonAdminForm
    list_display = ("title", "grade_ref", "subject_ref", "term", "caps_version", "is_published", "updated_at")
    list_filter = ("caps_version", "grade_ref", "subject_ref", "term", "is_published")
    search_fields = ("title", "topic", "content", "key_concepts", "examples", "summary")
    ordering = ("-updated_at",)
    list_editable = ("is_published",)

    def has_add_permission(self, request):
        from .utils import is_curriculum_admin
        return is_curriculum_admin(request.user)

    def has_change_permission(self, request, obj=None):
        from .utils import is_curriculum_admin
        if not is_curriculum_admin(request.user):
            return request.method in {"GET", "HEAD", "OPTIONS"}
        return True

    def has_delete_permission(self, request, obj=None):
        from .utils import is_curriculum_admin
        return is_curriculum_admin(request.user)


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
    list_display = ("number", "label", "phase")
    list_filter = ("phase",)
    ordering = ("number",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("caps_version", "grade", "subject", "is_published", "created_at")
    list_filter = ("caps_version", "grade", "subject", "is_published")
    search_fields = ("title", "description")


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("course", "user", "is_teacher", "is_active", "enrolled_at")
    list_filter = ("is_teacher", "is_active")
    search_fields = ("user__username", "course__subject__name")


@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ("course", "title", "created_by", "created_at", "is_published")
    list_filter = ("course", "is_published")
    search_fields = ("title", "message")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "resource_type", "caps_version", "grade", "subject", "is_published")
    list_filter = ("resource_type", "caps_version", "grade", "subject", "is_published")
    search_fields = ("title", "description")


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ("lesson", "resource")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "title", "created_at", "read_at")
    list_filter = ("read_at",)
    search_fields = ("title", "message")


@admin.register(CourseProgress)
class CourseProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "percent_complete", "updated_at")


@admin.register(CourseTermProgress)
class CourseTermProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "course", "term", "completed", "updated_at")
    list_filter = ("term", "completed")


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("user", "action", "course", "lesson", "created_at")
    list_filter = ("action",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("actor", "action", "target", "created_at")
    search_fields = ("action", "target")


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at")
    list_filter = ("role",)


@admin.register(CAPSVersion)
class CAPSVersionAdmin(admin.ModelAdmin):
    list_display = ("year", "description", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("year", "description")
    ordering = ("-year",)
    list_editable = ("is_active",)

    def has_add_permission(self, request):
        from .utils import is_curriculum_admin
        return is_curriculum_admin(request.user)

    def has_change_permission(self, request, obj=None):
        from .utils import is_curriculum_admin
        return is_curriculum_admin(request.user)

    def has_delete_permission(self, request, obj=None):
        from .utils import is_curriculum_admin
        return is_curriculum_admin(request.user)


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