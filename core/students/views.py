from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from core.accounts.decorators import student_required
from core.models import Lesson, Progress as LessonProgress


@login_required
@student_required
def student_dashboard(request):
    lessons = Lesson.published_for_active_caps().order_by("-created_at")
    return render(request, "students/dashboard.html", {
        "lessons": lessons,
    })


@login_required
@student_required
def student_progress(request):
    progress = LessonProgress.objects.filter(
        student=request.user,
        completed=True,
    ).select_related("lesson")
    return render(request, "students/progress.html", {
        "progress": progress,
    })
