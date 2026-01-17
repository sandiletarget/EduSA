from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractBaseUser


ROLE_DASHBOARD = {
    "student": "student_dashboard",
    "teacher": "teacher_dashboard",
}


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
