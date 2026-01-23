from django.contrib import admin

from .models import (
	Assessment,
	AssessmentSubmission,
	Class,
	ClassMembership,
	LiveSession,
	ChatMessage,
	Rubric,
	RubricCriterion,
	RubricScore,
	SubmissionComment,
)


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
	list_display = ("name", "teacher", "passcode", "created_at")
	list_filter = ("teacher",)
	search_fields = ("name", "description", "teacher__username")
	ordering = ("-created_at",)


@admin.register(ClassMembership)
class ClassMembershipAdmin(admin.ModelAdmin):
	list_display = ("learner", "classroom", "joined_at")
	search_fields = ("learner__username", "classroom__name")
	ordering = ("-joined_at",)


@admin.register(LiveSession)
class LiveSessionAdmin(admin.ModelAdmin):
	list_display = ("classroom", "is_active", "started_at")
	list_filter = ("is_active",)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
	list_display = ("title", "classroom", "teacher", "due_date", "allow_resubmission", "attempt_limit", "created_at")
	list_filter = ("teacher", "classroom", "allow_resubmission")
	search_fields = ("title", "instructions")
	ordering = ("-created_at",)


@admin.register(AssessmentSubmission)
class AssessmentSubmissionAdmin(admin.ModelAdmin):
	list_display = ("assessment", "student", "submitted_at", "mark", "graded_at", "attempt_number")
	list_filter = ("assessment", "graded_at")
	search_fields = ("student__username", "assessment__title")
	ordering = ("-submitted_at",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
	list_display = ("classroom", "sender", "created_at")
	list_filter = ("classroom",)
	search_fields = ("sender__username", "message")
	ordering = ("-created_at",)


class RubricCriterionInline(admin.TabularInline):
	model = RubricCriterion
	extra = 1


@admin.register(Rubric)
class RubricAdmin(admin.ModelAdmin):
	list_display = ("title", "created_at")
	search_fields = ("title", "description")
	inlines = [RubricCriterionInline]


@admin.register(RubricScore)
class RubricScoreAdmin(admin.ModelAdmin):
	list_display = ("submission", "criterion", "score", "graded_at")
	list_filter = ("criterion",)


@admin.register(SubmissionComment)
class SubmissionCommentAdmin(admin.ModelAdmin):
	list_display = ("submission", "author", "created_at")
	search_fields = ("comment",)
