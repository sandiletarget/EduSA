from io import BytesIO
import base64

import qrcode
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.core.exceptions import FieldDoesNotExist, PermissionDenied
from django.db.models import Avg
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from classes.models import Class as Classroom, ClassMembership
from core.models import Choice, Lesson, Question, Quiz, QuizResult

@login_required
def student_lesson_list(request):
    lessons = Lesson.objects.all().order_by('-created_at')
    return render(request, 'students/lesson_list.html', {
        'lessons': lessons
    })

@login_required
def student_lesson_detail(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    return render(request, 'students/lesson_detail.html', {
        'lesson': lesson
    })

@login_required
def take_quiz(request, lesson_id):
    quiz = get_object_or_404(Quiz, lesson_id=lesson_id)
    questions = Question.objects.filter(quiz=quiz)

    max_attempts = 3
    attempts = QuizResult.objects.filter(student=request.user, quiz=quiz).count()

    if attempts >= max_attempts:
        return render(request, 'students/quiz_limit.html', {
            'quiz': quiz,
            'max_attempts': max_attempts
        })

    if request.method == 'POST':
        score = 0
        total = questions.count()

        for question in questions:
            selected = request.POST.get(str(question.id))
            if not selected:
                continue

            choice = Choice.objects.filter(id=selected, question=question).first()
            if choice and choice.is_correct:
                score += 1

        percentage = int((score / total) * 100) if total else 0

        result = QuizResult.objects.create(
            student=request.user,
            quiz=quiz,
            score=percentage
        )

        return render(request, 'students/quiz_result.html', {
            'score': percentage,
            'result': result
        })

    return render(request, 'students/take_quiz.html', {
        'quiz': quiz,
        'questions': questions
    })


@login_required
def certificate_view(request, result_id):
    result = get_object_or_404(QuizResult, id=result_id, student=request.user)

    if result.score < 50:
        return HttpResponse("You did not pass this quiz.", status=403)

    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(result.certificate_code)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    html = f'''
<html>
<body style="text-align:center; padding:50px; font-family: Arial;">
<div style="border:5px solid #000; padding:40px;">
    <h1>Certificate of Completion</h1>

    <h2>{request.user.get_full_name() or request.user.username}</h2>
    <h3>{result.quiz.title}</h3>

    <p>Score: <strong>{result.score}%</strong></p>
    <p>Date: {timezone.now().date()}</p>

    <p>
        Certificate Code:<br>
        <strong>{result.certificate_code}</strong>
    </p>

    <p>Scan QR to verify:</p>
    <img src="data:image/png;base64,{qr_b64}" alt="QR Code">

    <br><br>
    <em>EduSA Learning Platform</em>
</div>
</body>
</html>
'''

    response = HttpResponse(html, content_type='text/html')
    response['Content-Disposition'] = 'inline; filename="certificate.html"'
    return response

@staff_member_required
def grade_level_analytics(request):
    # Get all grades from Lessons
    grades = Lesson.objects.values_list('grade', flat=True).distinct().order_by('grade')
    
    analytics_data = []

    for grade in grades:
        # Lessons for this grade
        lessons_in_grade = Lesson.objects.filter(grade=grade)

        # Total quiz results for these lessons
        quiz_results = QuizResult.objects.filter(quiz__lesson__in=lessons_in_grade)

        # Average score
        avg_score = quiz_results.aggregate(Avg('score'))['score__avg'] or 0

        # Completion / Attempts count
        total_attempts = quiz_results.count()
        total_passed = quiz_results.filter(score__gte=50).count()
        total_failed = total_attempts - total_passed

        analytics_data.append({
            'grade': grade,
            'avg_score': round(avg_score, 2),
            'total_attempts': total_attempts,
            'passed': total_passed,
            'failed': total_failed
        })

    return render(request, 'teachers/grade_analytics.html', {
        'analytics_data': analytics_data
    })


@login_required
def class_lesson_list(request, class_id):
    classroom = get_object_or_404(Classroom, pk=class_id)
    is_teacher = request.user == classroom.teacher
    membership = ClassMembership.objects.filter(classroom=classroom, learner=request.user).exists()

    if not (is_teacher or membership):
        raise PermissionDenied

    lessons = Lesson.objects.filter(classroom=classroom)
    try:
        Lesson._meta.get_field('is_published')
        if not is_teacher:
            lessons = lessons.filter(is_published=True)
    except FieldDoesNotExist:
        if not is_teacher:
            lessons = lessons
    lessons = lessons.order_by('-created_at')
    prepared_lessons = []
    for lesson in lessons:
        published = getattr(lesson, 'is_published', True)
        lesson.status_label = 'Published' if published else 'Draft'
        prepared_lessons.append(lesson)

    return render(request, 'lessons/lesson_list.html', {
        'classroom': classroom,
        'lessons': prepared_lessons,
        'is_teacher': is_teacher,
    })
