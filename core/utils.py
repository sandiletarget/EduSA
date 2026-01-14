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


def dashboard_for_user(user: "AbstractBaseUser") -> str | None:
    return ROLE_DASHBOARD.get(normalize_role(getattr(user, "role", None)))
