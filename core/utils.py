from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


ROLE_DASHBOARD = {
    "student": "student_dashboard",
    "teacher": "teacher_dashboard",
}


def is_curriculum_admin(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    if hasattr(user, "groups") and user.groups.filter(name="Curriculum Admins").exists():
        return True
    return False


def normalize_role(role: str | None) -> str:
    return (role or "").strip().lower()


def resolve_user_role(user: "AbstractBaseUser") -> str:
    role = normalize_role(getattr(user, "role", None))
    if role:
        return role

    if getattr(user, "is_staff", False):
        return "teacher"

    if hasattr(user, "groups"):
        if user.groups.filter(name="Students").exists():
            return "student"
        if user.groups.filter(name="Teachers").exists():
            return "teacher"

    return ""


def dashboard_for_user(user: "AbstractBaseUser") -> str | None:
    return ROLE_DASHBOARD.get(resolve_user_role(user))


def clone_caps_lessons(source_version, target_version, *, publish=False):
    from core.models import Lesson

    source_lessons = Lesson.objects.filter(caps_version=source_version)
    new_lessons = []
    for lesson in source_lessons:
        new_lessons.append(
            Lesson(
                caps_version=target_version,
                title=lesson.title,
                slug=None,
                term=lesson.term,
                topic=lesson.topic,
                content=lesson.content,
                key_concepts=lesson.key_concepts,
                examples=lesson.examples,
                summary=lesson.summary,
                grade=lesson.grade,
                subject=lesson.subject,
                grade_ref=lesson.grade_ref,
                subject_ref=lesson.subject_ref,
                topic_ref=lesson.topic_ref,
                subtopic_ref=lesson.subtopic_ref,
                notes_text=lesson.notes_text,
                notes_file=lesson.notes_file,
                video_url=lesson.video_url,
                formula_sheet=lesson.formula_sheet,
                cover_image=lesson.cover_image,
                is_published=publish,
            )
        )
    return Lesson.objects.bulk_create(new_lessons)


def course_for_lesson(lesson):
    from core.models import Course

    if not lesson.caps_version or not lesson.grade_ref or not lesson.subject_ref:
        return None
    return Course.objects.filter(
        caps_version=lesson.caps_version,
        grade=lesson.grade_ref,
        subject=lesson.subject_ref,
    ).first()
