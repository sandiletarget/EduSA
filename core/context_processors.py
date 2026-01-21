from .models import Grade


def grade_nav_context(request):
    grades = list(Grade.objects.order_by("number"))
    return {
        "nav_grades": grades,
    }
