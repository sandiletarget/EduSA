from django.contrib.auth.decorators import user_passes_test

from core.utils import resolve_user_role


def student_required(view_func):
    def _is_student(user):
        if not user.is_authenticated:
            return False
        role = resolve_user_role(user)
        return role == "student" if role else not getattr(user, "is_staff", False)

    return user_passes_test(_is_student)(view_func)
