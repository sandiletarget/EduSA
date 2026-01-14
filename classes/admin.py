from django.contrib import admin

from .models import Class, ClassMembership, LiveSession


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
