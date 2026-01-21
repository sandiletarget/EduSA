from django.contrib import admin

from .models import Assessment, AssessmentSubmission, Class, ClassMembership, LiveSession


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
	list_display = ("title", "classroom", "teacher", "due_date", "created_at")
	list_filter = ("teacher", "classroom")
	search_fields = ("title", "instructions")
	ordering = ("-created_at",)


@admin.register(AssessmentSubmission)
class AssessmentSubmissionAdmin(admin.ModelAdmin):
	list_display = ("assessment", "student", "submitted_at")
	list_filter = ("assessment",)
	search_fields = ("student__username", "assessment__title")
	ordering = ("-submitted_at",)
