from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from core.accounts.decorators import student_required
from core.models import Lesson, Progress as LessonProgress


@login_required
@student_required
def student_lesson_list(request):
    lessons = Lesson.objects.all().order_by('-created_at')
    return render(request, 'students/lesson_list.html', {
        'lessons': lessons
    })


@login_required
@student_required
def student_lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    progress = LessonProgress.objects.filter(
        student=request.user,
        lesson=lesson
    ).first()
    return render(request, 'students/lesson_detail.html', {
        'lesson': lesson,
        'progress': progress
    })


@login_required
@student_required
def mark_lesson_complete(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    progress, created = LessonProgress.objects.get_or_create(
        student=request.user,
        lesson=lesson,
    )

    progress.completed = True
    progress.completed_at = timezone.now()
    progress.mark = max(progress.mark, 100)
    progress.save()

    return redirect('student_lesson_detail', pk=pk)
 